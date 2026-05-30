from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.request_context import get_request_context
from app.models import AuditLog, User
from app.repositories.audit import AuditRepository
from app.repositories.task import TaskRepository
from app.repositories.user import UserRepository
from app.schemas.admin import (
    AdminOverviewResponse,
    AdminUsersResponse,
    AuditEventsResponse,
    MonitoringLinks,
    NamedMetric,
)
from app.schemas.task import PaginationMeta


class AuditService:
    def __init__(self, session: Session):
        self.session = session
        self.audit = AuditRepository(session)
        self.users = UserRepository(session)
        self.tasks = TaskRepository(session)

    def record_event(
        self,
        action: str,
        category: str,
        user: Optional[User] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        status_code: int = 200,
        duration_ms: int = 0,
        details: Optional[dict[str, Any]] = None,
        request_override: Optional[dict[str, Optional[str]]] = None,
        commit: bool = True,
    ) -> AuditLog:
        request_context = get_request_context()
        audit_log = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            role=user.role if user else None,
            category=category,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            method=request_override.get("method") if request_override else (request_context.method if request_context else "SYSTEM"),
            path=request_override.get("path") if request_override else (request_context.path if request_context else "system"),
            query_string=request_override.get("query_string") if request_override else (request_context.query_string if request_context else None),
            client_ip=request_override.get("client_ip") if request_override else (request_context.client_ip if request_context else None),
            user_agent=request_override.get("user_agent") if request_override else (request_context.user_agent if request_context else None),
            request_id=request_override.get("request_id") if request_override else (request_context.request_id if request_context else None),
            status_code=status_code,
            duration_ms=duration_ms,
            details=details,
        )
        created_log = self.audit.add(audit_log)
        if commit:
            self.session.commit()
        return created_log

    def build_overview(self) -> AdminOverviewResponse:
        role_counts = [NamedMetric(label=label, value=value) for label, value in self.users.count_by_role()]
        all_users = self.users.list_users()
        task_totals = {"total": 0, "todo": 0, "done": 0, "archived": 0}
        for user in all_users:
            summary = self.tasks.summary_for_user(user.id)
            for key, value in summary.items():
                task_totals[key] += value

        return AdminOverviewResponse(
            monitoring=MonitoringLinks(
                grafana=settings.grafana_url,
                prometheus=settings.prometheus_url,
                loki=settings.loki_url,
                pgadmin=settings.pgadmin_url,
            ),
            role_counts=role_counts,
            task_counts=[NamedMetric(label=key, value=value) for key, value in task_totals.items()],
            request_volume=[NamedMetric(label=label, value=value) for label, value in self.audit.requests_by_day()],
            action_breakdown=[NamedMetric(label=label, value=value) for label, value in self.audit.actions_breakdown()],
            status_breakdown=[NamedMetric(label=label, value=value) for label, value in self.audit.status_breakdown()],
            top_paths=[NamedMetric(label=label, value=value) for label, value in self.audit.top_paths()],
        )

    def list_events(
        self,
        page: int,
        page_size: int,
        category: Optional[str] = None,
        action: Optional[str] = None,
    ) -> AuditEventsResponse:
        items, total = self.audit.list_events(page=page, page_size=page_size, category=category, action=action)
        return AuditEventsResponse(
            items=[
                {
                    "id": item.id,
                    "category": item.category,
                    "action": item.action,
                    "path": item.path,
                    "method": item.method,
                    "status_code": item.status_code,
                    "duration_ms": item.duration_ms,
                    "username": item.username,
                    "role": item.role,
                    "client_ip": item.client_ip,
                    "request_id": item.request_id,
                    "created_at": item.created_at,
                    "details": item.details,
                }
                for item in items
            ],
            meta=PaginationMeta.build(
                page=page,
                page_size=page_size,
                total_items=total,
                sort_by="created_at",
                sort_order="desc",
            ),
        )

    def list_users(self, page: int, page_size: int) -> AdminUsersResponse:
        users = self.users.list_users()
        total = len(users)
        start = (page - 1) * page_size
        paginated_users = users[start : start + page_size]
        return AdminUsersResponse(
            items=[
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "task_summary": self.tasks.summary_for_user(user.id),
                }
                for user in paginated_users
            ],
            meta=PaginationMeta.build(
                page=page,
                page_size=page_size,
                total_items=total,
                sort_by="created_at",
                sort_order="desc",
            ),
        )
