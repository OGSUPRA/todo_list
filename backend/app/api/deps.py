from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.security import decode_token
from app.models import User
from app.repositories.user import UserRepository

DBSession = Annotated[Session, Depends(get_db_session)]


def _extract_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Требуется авторизация")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный формат токена")
    return token


def get_current_user(
    session: DBSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    token = _extract_token(authorization)
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный access token")

    user = UserRepository(session).get_by_id(uuid.UUID(payload["sub"]))
    if user is None or user.token_version != payload.get("tv"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия устарела")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
