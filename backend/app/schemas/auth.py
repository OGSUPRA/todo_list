from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import PublicRole


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: PublicRole = "standard"


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class TokenPayload(BaseModel):
    access_token: str
    token_type: str = "bearer"
