from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.task import PaginationMeta


class MonitoringLinks(BaseModel):
    dozzle: str
    pgweb: str


class NamedMetric(BaseModel):
    label: str
    value: int


class AuditEventResponse(BaseModel):
    id: uuid.UUID
    category: str
    action: str
    path: str
    method: str
    status_code: int
    duration_ms: int
    username: Optional[str]
    role: Optional[str]
    client_ip: Optional[str]
    request_id: Optional[str]
    created_at: datetime
    details: Optional[dict]


class AuditEventsResponse(BaseModel):
    items: list[AuditEventResponse]
    meta: PaginationMeta


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    task_summary: dict[str, int]


class AdminUsersResponse(BaseModel):
    items: list[AdminUserResponse]
    meta: PaginationMeta


class AdminOverviewResponse(BaseModel):
    monitoring: MonitoringLinks
    role_counts: list[NamedMetric]
    task_counts: list[NamedMetric]
    request_volume: list[NamedMetric]
    action_breakdown: list[NamedMetric]
    status_breakdown: list[NamedMetric]
    top_paths: list[NamedMetric]
