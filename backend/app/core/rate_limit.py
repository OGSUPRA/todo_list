from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import time
from typing import Deque

from starlette.requests import Request

from app.core.config import settings


@dataclass(frozen=True)
class RateLimitRule:
    limit: int
    window_seconds: int
    name: str


_requests: dict[str, Deque[float]] = defaultdict(deque)
_lock = Lock()


def _parse_rate_limit(value: str, name: str) -> RateLimitRule:
    amount, _, window = value.partition("/")
    window_seconds = {
        "second": 1,
        "minute": 60,
        "hour": 3600,
    }[window]
    return RateLimitRule(limit=int(amount), window_seconds=window_seconds, name=name)


AUTH_RULE = _parse_rate_limit(settings.auth_rate_limit, "auth")
WRITE_RULE = _parse_rate_limit(settings.write_rate_limit, "write")
READ_RULE = _parse_rate_limit(settings.read_rate_limit, "read")


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def get_rate_limit_rule(request: Request) -> RateLimitRule:
    path = request.url.path
    if path.startswith("/api/v1/auth/login") or path.startswith("/api/v1/auth/register") or path.startswith("/api/v1/auth/refresh"):
        return AUTH_RULE
    if request.method in {"POST", "PATCH", "DELETE", "PUT"}:
        return WRITE_RULE
    return READ_RULE


def check_rate_limit(request: Request) -> tuple[bool, RateLimitRule, int, int]:
    rule = get_rate_limit_rule(request)
    key = f"{rule.name}:{request.method}:{request.url.path}:{get_client_ip(request)}"
    now = time()

    with _lock:
        bucket = _requests[key]
        while bucket and now - bucket[0] >= rule.window_seconds:
            bucket.popleft()

        if len(bucket) >= rule.limit:
            reset_after = max(0, int(rule.window_seconds - (now - bucket[0]))) if bucket else rule.window_seconds
            return False, rule, 0, reset_after

        bucket.append(now)
        remaining = max(0, rule.limit - len(bucket))
        return True, rule, remaining, rule.window_seconds


def reset_rate_limits() -> None:
    with _lock:
        _requests.clear()
