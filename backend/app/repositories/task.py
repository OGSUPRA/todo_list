from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def list_for_user(
        self,
        user_id: uuid.UUID,
        include_deleted: bool,
        only_deleted: bool,
        status: Optional[str],
        search: Optional[str],
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> tuple[list[Task], int]:
        statement: Select[tuple[Task]] = select(Task).where(Task.user_id == user_id)
        count_statement = select(func.count(Task.id)).where(Task.user_id == user_id)
        if only_deleted:
            statement = statement.where(Task.is_deleted.is_(True))
            count_statement = count_statement.where(Task.is_deleted.is_(True))
        elif not include_deleted:
            statement = statement.where(Task.is_deleted.is_(False))
            count_statement = count_statement.where(Task.is_deleted.is_(False))
        if status:
            statement = statement.where(Task.status == status)
            count_statement = count_statement.where(Task.status == status)
        if search:
            search_term = f"%{search}%"
            statement = statement.where(Task.title.ilike(search_term) | Task.description.ilike(search_term))
            count_statement = count_statement.where(Task.title.ilike(search_term) | Task.description.ilike(search_term))

        sort_column = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "status": Task.status,
        }.get(sort_by, Task.created_at)
        sort_expression = sort_column.asc() if sort_order == "asc" else sort_column.desc()

        total = int(self.session.execute(count_statement).scalar_one())
        items = list(
            self.session.execute(
                statement.order_by(sort_expression).offset((page - 1) * page_size).limit(page_size)
            ).scalars().all()
        )
        return items, total

    def get_for_user(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return self.session.execute(statement).scalar_one_or_none()

    def add(self, task: Task) -> Task:
        self.session.add(task)
        self.session.flush()
        self.session.refresh(task)
        return task

    def summary_for_user(self, user_id: uuid.UUID) -> dict[str, int]:
        statement = (
            select(
                func.count(Task.id).label("total"),
                func.sum(case((Task.status == "todo", 1), else_=0)).label("todo"),
                func.sum(case((Task.status == "done", 1), else_=0)).label("done"),
                func.sum(case((Task.is_deleted.is_(True), 1), else_=0)).label("archived"),
            )
            .where(Task.user_id == user_id)
        )
        total, todo, done, archived = self.session.execute(statement).one()
        return {
            "total": int(total or 0),
            "todo": int(todo or 0),
            "done": int(done or 0),
            "archived": int(archived or 0),
        }
