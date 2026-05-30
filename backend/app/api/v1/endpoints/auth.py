from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.deps import DBSession, CurrentUser
from app.core.config import settings
from app.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPayload
from app.schemas.common import APIMessage
from app.schemas.user import UserResponse
from app.services.auth import AuthService

router = APIRouter()


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=int(timedelta(days=settings.refresh_token_ttl_days).total_seconds()),
        path="/api/v1/auth",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, session: DBSession) -> User:
    return AuthService(session).register(payload)


@router.post("/login", response_model=TokenPayload)
def login(payload: LoginRequest, response: Response, session: DBSession) -> TokenPayload:
    service = AuthService(session)
    user = service.authenticate(payload)
    token_payload, refresh_token = service.build_token_pair(user)
    _set_refresh_cookie(response, refresh_token)
    return token_payload


@router.post("/refresh", response_model=TokenPayload)
def refresh(request: Request, response: Response, session: DBSession) -> TokenPayload:
    refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token:
        response.delete_cookie(settings.refresh_cookie_name, path="/api/v1/auth")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token отсутствует")

    user = AuthService(session).validate_refresh_token(refresh_token)
    token_payload, new_refresh_token = AuthService(session).build_token_pair(user)
    _set_refresh_cookie(response, new_refresh_token)
    return token_payload


@router.post("/logout", response_model=APIMessage)
def logout(current_user: CurrentUser, response: Response, session: DBSession) -> APIMessage:
    current_user.token_version += 1
    session.commit()
    response.delete_cookie(settings.refresh_cookie_name, path="/api/v1/auth")
    return APIMessage(detail="Вы вышли из системы")


@router.get("/me", response_model=UserResponse)
def me(current_user: CurrentUser) -> User:
    return current_user
