from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_user(
        self,
        user_id: uuid.UUID,
        include_deleted: bool,
        status: str | None,
        search: str | None,
    ) -> list[Task]:
        statement: Select[tuple[Task]] = select(Task).where(Task.user_id == user_id)
        if not include_deleted:
            statement = statement.where(Task.is_deleted.is_(False))
        if status:
            statement = statement.where(Task.status == status)
        if search:
            statement = statement.where(Task.title.ilike(f"%{search}%"))
        statement = statement.order_by(Task.created_at.desc())
        return list(self.session.execute(statement).scalars().all())

    def get_for_user(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task | None:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.session.execute(statement).scalar_one_or_none()

    def add(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        self.session.refresh(task)
        return task
