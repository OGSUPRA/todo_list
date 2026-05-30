from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Request

from app.api.deps import CurrentAdmin, DBSession
from app.schemas.admin import AdminOverviewResponse, AdminUsersResponse, AuditEventsResponse
from app.services.audit import AuditService

router = APIRouter()


@router.get("/overview", response_model=AdminOverviewResponse)
def get_admin_overview(request: Request, session: DBSession, current_admin: CurrentAdmin) -> AdminOverviewResponse:
    return AuditService(session).build_overview()


@router.get("/audit-events", response_model=AuditEventsResponse)
def list_audit_events(
    request: Request,
    session: DBSession,
    current_admin: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(default=None),
    action: Optional[str] = Query(default=None),
) -> AuditEventsResponse:
    return AuditService(session).list_events(page=page, page_size=page_size, category=category, action=action)


@router.get("/users", response_model=AdminUsersResponse)
def list_admin_users(
    request: Request,
    session: DBSession,
    current_admin: CurrentAdmin,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> AdminUsersResponse:
    return AuditService(session).list_users(page=page, page_size=page_size)
