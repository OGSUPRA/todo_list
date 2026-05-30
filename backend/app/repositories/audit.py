from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import String, cast, func, select
from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, audit_log: AuditLog) -> AuditLog:
        self.session.add(audit_log)
        self.session.flush()
        return audit_log

    def list_events(
        self,
        page: int,
        page_size: int,
        category: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[list[AuditLog], int]:
        statement = select(AuditLog)
        count_statement = select(func.count(AuditLog.id))

        if category:
            statement = statement.where(AuditLog.category == category)
            count_statement = count_statement.where(AuditLog.category == category)
        if action:
            statement = statement.where(AuditLog.action == action)
            count_statement = count_statement.where(AuditLog.action == action)

        total = int(self.session.execute(count_statement).scalar_one())
        items = list(
            self.session.execute(
                statement.order_by(AuditLog.created_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).scalars()
        )
        return items, total

    def requests_by_day(self, days: int = 7) -> list[tuple[str, int]]:
        statement = (
            select(
                func.date(AuditLog.created_at).label("day"),
                func.count(AuditLog.id).label("count"),
            )
            .group_by(func.date(AuditLog.created_at))
            .order_by(func.date(AuditLog.created_at))
        )
        return [(str(day), int(count)) for day, count in self.session.execute(statement).all()][-days:]

    def actions_breakdown(self, limit: int = 8) -> list[tuple[str, int]]:
        statement = (
            select(AuditLog.action, func.count(AuditLog.id).label("count"))
            .group_by(AuditLog.action)
            .order_by(func.count(AuditLog.id).desc())
            .limit(limit)
        )
        return [(action, int(count)) for action, count in self.session.execute(statement).all()]

    def status_breakdown(self) -> list[tuple[str, int]]:
        statement = (
            select(
                func.substr(cast(AuditLog.status_code, String), 1, 1).label("bucket"),
                func.count(AuditLog.id).label("count"),
            )
            .group_by(func.substr(cast(AuditLog.status_code, String), 1, 1))
            .order_by(func.substr(cast(AuditLog.status_code, String), 1, 1))
        )
        return [(f"{bucket}xx", int(count)) for bucket, count in self.session.execute(statement).all()]

    def top_paths(self, limit: int = 10) -> list[tuple[str, int]]:
        statement = (
            select(AuditLog.path, func.count(AuditLog.id).label("count"))
            .group_by(AuditLog.path)
            .order_by(func.count(AuditLog.id).desc())
            .limit(limit)
        )
        return [(path, int(count)) for path, count in self.session.execute(statement).all()]
