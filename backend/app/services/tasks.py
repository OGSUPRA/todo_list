from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Task
from app.repositories.task import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, session: Session):
        self.session = session
        self.tasks = TaskRepository(session)

    def list_tasks(
        self,
        user_id: uuid.UUID,
        include_deleted: bool = False,
        status_filter: str | None = None,
        search: str | None = None,
    ) -> list[Task]:
        return self.tasks.list_for_user(user_id, include_deleted=include_deleted, status=status_filter, search=search)

    def create_task(self, user_id: uuid.UUID, payload: TaskCreate) -> Task:
        task = Task(user_id=user_id, title=payload.title.strip(), description=payload.description.strip())
        created_task = self.tasks.add(task)
        self.session.commit()
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
        return task

    def toggle_task_status(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self._get_task(task_id, user_id)
        task.status = "done" if task.status == "todo" else "todo"
        self.session.commit()
        self.session.refresh(task)
        return task

    def mark_all_done(self, user_id: uuid.UUID) -> None:
        tasks = self.tasks.list_for_user(user_id, include_deleted=False, status="todo", search=None)
        for task in tasks:
            task.status = "done"
        self.session.commit()

    def soft_delete(self, task_id: uuid.UUID, user_id: uuid.UUID) -> None:
        task = self._get_task(task_id, user_id)
        task.is_deleted = True
        self.session.commit()

    def restore(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self._get_task(task_id, user_id)
        task.is_deleted = False
        self.session.commit()
        self.session.refresh(task)
        return task

    def _get_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task:
        task = self.tasks.get_for_user(task_id, user_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
        return task
