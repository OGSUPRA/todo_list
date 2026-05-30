from __future__ import annotations

import uuid
from datetime import datetime
from math import ceil
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=5000)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=180)
    description: Optional[str] = Field(default=None, max_length=5000)
    status: Optional[str] = Field(default=None, pattern="^(todo|done)$")


class TaskResponse(ORMModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
    sort_by: str
    sort_order: str

    @classmethod
    def build(
        cls,
        page: int,
        page_size: int,
        total_items: int,
        sort_by: str,
        sort_order: str,
    ) -> "PaginationMeta":
        total_pages = max(1, ceil(total_items / page_size)) if page_size else 1
        return cls(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
            sort_by=sort_by,
            sort_order=sort_order,
        )


class TaskSummary(BaseModel):
    total: int
    todo: int
    done: int
    archived: int


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    meta: PaginationMeta
    summary: TaskSummary
