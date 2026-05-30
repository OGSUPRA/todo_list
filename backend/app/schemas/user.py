from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class UserResponse(ORMModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    avatar_path: Optional[str]
    created_at: datetime


class UserUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
