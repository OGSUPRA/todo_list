from __future__ import annotations

import uuid
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPayload


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)

    def register(self, payload: RegisterRequest) -> User:
        if self.users.get_by_username(payload.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Имя пользователя уже занято")
        if self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже используется")

        user = User(
            username=payload.username,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )
        created_user = self.users.add(user)
        self.session.commit()
        return created_user

    def authenticate(self, payload: LoginRequest) -> User:
        user = self.users.get_by_username_or_email(payload.username)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Пользователь деактивирован")
        return user

    def build_token_pair(self, user: User) -> tuple[TokenPayload, str]:
        claims = {"tv": user.token_version}
        access_token = create_token(
            subject=str(user.id),
            token_type="access",
            expires_delta=timedelta(minutes=settings.access_token_ttl_minutes),
            extra_claims=claims,
        )
        refresh_token = create_token(
            subject=str(user.id),
            token_type="refresh",
            expires_delta=timedelta(days=settings.refresh_token_ttl_days),
            extra_claims=claims,
        )
        return TokenPayload(access_token=access_token), refresh_token

    def validate_refresh_token(self, token: str) -> User:
        try:
            payload = decode_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный refresh token")

        user = self.users.get_by_id(uuid.UUID(payload["sub"]))
        if user is None or user.token_version != payload.get("tv"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия устарела")
        return user
