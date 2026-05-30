from __future__ import annotations

import uuid
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Task
from app.repositories.task import TaskRepository
from app.schemas.task import PaginationMeta, TaskCreate, TaskListResponse, TaskSummary, TaskUpdate
from app.services.audit import AuditService


class TaskService:
    def __init__(self, session: Session):
        self.session = session
        self.tasks = TaskRepository(session)

    def list_tasks(
        self,
        user_id: uuid.UUID,
        include_deleted: bool = False,
        only_deleted: bool = False,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> TaskListResponse:
        items, total = self.tasks.list_for_user(
            user_id,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
            status=status_filter,
            search=search,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        summary = self.tasks.summary_for_user(user_id)
        return TaskListResponse(
            items=items,
            meta=PaginationMeta.build(
                page=page,
                page_size=page_size,
                total_items=total,
                sort_by=sort_by,
                sort_order=sort_order,
            ),
            summary=TaskSummary(**summary),
        )

    def create_task(self, user_id: uuid.UUID, payload: TaskCreate) -> Task:
        task = Task(user_id=user_id, title=payload.title.strip(), description=payload.description.strip())
        created_task = self.tasks.add(task)
        self.session.commit()
        user = self._get_user(user_id)
        AuditService(self.session).record_event(
            action="task.create",
            category="task",
            user=user,
            entity_type="task",
            entity_id=str(created_task.id),
            details={"title": created_task.title},
        )
        return created_task

    def update_task(self, task_id: uuid.UUID, user_id: uuid.UUID, payload: TaskUpdate) -> Task:
        task = self._get_task(task_id, user_id)
        if payload.title is not None:
            task.title = payload.title.strip()
        if payload.description is not None:
            task.description = payload.description.strip()
        if payload.status is not None:
            task.status = payload.status
        self.session.commit()
        self.session.refresh(task)
        user = self._get_user(user_id)
        AuditService(self.session).record_event(
            action="task.update",
            category="task",
            user=user,
            entity_type="task",
            entity_id=str(task.id),
            details={"status": task.status, "title": task.title},
        )
        return task

    def toggle_task_status(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self._get_task(task_id, user_id)
        task.status = "done" if task.status == "todo" else "todo"
        self.session.commit()
        self.session.refresh(task)
        user = self._get_user(user_id)
        AuditService(self.session).record_event(
            action="task.toggle",
            category="task",
            user=user,
            entity_type="task",
            entity_id=str(task.id),
            details={"status": task.status},
        )
        return task

    def mark_all_done(self, user_id: uuid.UUID) -> None:
        items, _ = self.tasks.list_for_user(
            user_id,
            include_deleted=False,
            only_deleted=False,
            status="todo",
            search=None,
            page=1,
            page_size=1000,
            sort_by="created_at",
            sort_order="desc",
        )
        for task in items:
            task.status = "done"
        self.session.commit()
        user = self._get_user(user_id)
        AuditService(self.session).record_event(
            action="task.mark_all_done",
            category="task",
            user=user,
            entity_type="task",
            details={"count": len(items)},
        )

    def soft_delete(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        task = self._get_task(task_id, user_id)
        task.is_deleted = True
        self.session.commit()
        user = self._get_user(user_id)
        AuditService(self.session).record_event(
            action="task.archive",
            category="task",
            user=user,
            entity_type="task",
            entity_id=str(task.id),
            details={"title": task.title},
        )

    def restore(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self._get_task(task_id, user_id)
        task.is_deleted = False
        self.session.commit()
        self.session.refresh(task)
        user = self._get_user(user_id)
        AuditService(self.session).record_event(
            action="task.restore",
            category="task",
            user=user,
            entity_type="task",
            entity_id=str(task.id),
            details={"title": task.title},
        )
        return task

    def _get_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self.tasks.get_for_user(task_id, user_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        return task

    def _get_user(self, user_id: uuid.UUID):
        from app.repositories.user import UserRepository

        return UserRepository(self.session).get_by_id(user_id)
