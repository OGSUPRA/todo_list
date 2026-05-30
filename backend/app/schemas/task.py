from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(default="", max_length=5000)


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    description: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, pattern="^(todo|done)$")


class TaskResponse(ORMModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
