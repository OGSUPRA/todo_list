from __future__ import annotations

import uuid
from typing import Optional
from fastapi import APIRouter, Query, Request, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.common import APIMessage
from app.schemas.task import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from app.services.tasks import TaskService

router = APIRouter()


@router.get("", response_model=TaskListResponse)
def list_tasks(
    request: Request,
    session: DBSession,
    current_user: CurrentUser,
    include_deleted: bool = Query(default=False),
    only_deleted: bool = Query(default=False),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="created_at", pattern="^(created_at|updated_at|title|status)$"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> TaskListResponse:
    return TaskService(session).list_tasks(
        current_user.id,
        include_deleted=include_deleted,
        only_deleted=only_deleted,
        status_filter=status_filter,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(request: Request, payload: TaskCreate, session: DBSession, current_user: CurrentUser) -> TaskResponse:
    return TaskService(session).create_task(current_user.id, payload)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    request: Request,
    task_id: uuid.UUID,
    payload: TaskUpdate,
    session: DBSession,
    current_user: CurrentUser,
) -> TaskResponse:
    return TaskService(session).update_task(task_id, current_user.id, payload)


@router.post("/{task_id}/toggle", response_model=TaskResponse)
def toggle_task(request: Request, task_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> TaskResponse:
    return TaskService(session).toggle_task_status(task_id, current_user.id)


@router.post("/mark-all-done", response_model=APIMessage)
def mark_all_done(request: Request, session: DBSession, current_user: CurrentUser) -> APIMessage:
    TaskService(session).mark_all_done(current_user.id)
    return APIMessage(detail="Все задачи переведены в статус выполнено")


@router.delete("/{task_id}", response_model=APIMessage)
def delete_task(request: Request, task_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> APIMessage:
    TaskService(session).soft_delete(task_id, current_user.id)
    return APIMessage(detail="Задача отправлена в архив")


@router.post("/{task_id}/restore", response_model=TaskResponse)
def restore_task(request: Request, task_id: uuid.UUID, session: DBSession, current_user: CurrentUser) -> TaskResponse:
    return TaskService(session).restore(task_id, current_user.id)
