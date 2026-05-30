from __future__ import annotations

from pathlib import Path
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import SessionLocal, ping_database
from app.core.rate_limit import check_rate_limit
from app.core.request_context import RequestContext, request_context_var
from app.core.security import decode_token
from app.models import User
from app.repositories.user import UserRepository
from app.services.audit import AuditService

Path(settings.media_root).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Path(settings.media_root).mkdir(parents=True, exist_ok=True)
    ping_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.metrics_enabled:
    Instrumentator(excluded_handlers=["/api/metrics"]).instrument(app).expose(
        app,
        endpoint="/api/metrics",
        include_in_schema=False,
    )


def _resolve_user_for_request(request: Request) -> Optional[User]:
    authorization = request.headers.get("authorization")
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    try:
        payload = decode_token(token)
    except ValueError:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    try:
        user_uuid = UUID(str(user_id))
    except ValueError:
        return None

    session = SessionLocal()
    try:
        return UserRepository(session).get_by_id(user_uuid)
    finally:
        session.close()


@app.middleware("http")
async def audit_requests(request: Request, call_next):
    request_id = str(uuid4())
    started_at = perf_counter()
    request_context = RequestContext(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query_string=request.url.query,
        client_ip=request.headers.get("x-forwarded-for", request.client.host if request.client else None),
        user_agent=request.headers.get("user-agent"),
    )
    token = request_context_var.set(request_context)

    allowed, rule, remaining, reset_after = check_rate_limit(request)
    if not allowed:
        session = SessionLocal()
        try:
            AuditService(session).record_event(
                action="http.rate_limited",
                category="security",
                user=_resolve_user_for_request(request),
                status_code=429,
                duration_ms=0,
                details={"rule": rule.name, "path": request.url.path},
            )
        finally:
            session.close()
            request_context_var.reset(token)

        response = JSONResponse(status_code=429, content={"detail": "Слишком много запросов. Попробуйте позже."})
        response.headers["X-RateLimit-Limit"] = str(rule.limit)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["Retry-After"] = str(reset_after)
        response.headers["X-Request-ID"] = request_id
        return response

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((perf_counter() - started_at) * 1000)
        session = SessionLocal()
        try:
            AuditService(session).record_event(
                action="http.request",
                category="request",
                user=_resolve_user_for_request(request),
                status_code=500,
                duration_ms=duration_ms,
                details={"query": request.url.query},
                commit=True,
            )
        finally:
            session.close()
            request_context_var.reset(token)
        raise

    duration_ms = int((perf_counter() - started_at) * 1000)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-RateLimit-Limit"] = str(rule.limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    session = SessionLocal()
    try:
        AuditService(session).record_event(
            action="http.request",
            category="request",
            user=_resolve_user_for_request(request),
            status_code=response.status_code,
            duration_ms=duration_ms,
            details={"query": request.url.query},
            commit=True,
        )
    finally:
        session.close()
        request_context_var.reset(token)

    return response

app.mount("/media", StaticFiles(directory=settings.media_root), name="media")
app.include_router(api_router, prefix="/api")
