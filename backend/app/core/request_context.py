from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestContext:
    request_id: str
    method: str
    path: str
    query_string: str
    client_ip: Optional[str]
    user_agent: Optional[str]


request_context_var: ContextVar[Optional[RequestContext]] = ContextVar("request_context", default=None)


def get_request_context() -> Optional[RequestContext]:
    return request_context_var.get()
