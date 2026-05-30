from __future__ import annotations

import uuid
from fastapi import APIRouter, File, Request, UploadFile

from app.api.deps import CurrentAdmin, CurrentUser, DBSession
from app.schemas.common import APIMessage
from app.schemas.user import PasswordChangeRequest, UserResponse, UserRoleUpdateRequest, UserUpdate
from app.services.users import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(request: Request, current_user: CurrentUser) -> UserResponse:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(request: Request, payload: UserUpdate, session: DBSession, current_user: CurrentUser) -> UserResponse:
    return UserService(session).update_profile(current_user, payload)


@router.post("/me/avatar", response_model=UserResponse)
async def update_avatar(
    request: Request,
    session: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> UserResponse:
    return await UserService(session).update_avatar(current_user, file)


@router.post("/me/password", response_model=APIMessage)
def change_password(
    request: Request,
    payload: PasswordChangeRequest,
    session: DBSession,
    current_user: CurrentUser,
) -> APIMessage:
    UserService(session).change_password(current_user, payload)
    return APIMessage(detail="Пароль обновлен. Войдите заново на всех устройствах")


@router.delete("/me", response_model=APIMessage)
def delete_me(request: Request, session: DBSession, current_user: CurrentUser) -> APIMessage:
    UserService(session).delete_account(current_user)
    return APIMessage(detail="Аккаунт удален")


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    request: Request,
    user_id: uuid.UUID,
    payload: UserRoleUpdateRequest,
    session: DBSession,
    current_admin: CurrentAdmin,
) -> UserResponse:
    return UserService(session).update_role(user_id, payload, current_admin)
