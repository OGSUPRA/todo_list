from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from app.api.deps import CurrentUser, DBSession
from app.schemas.common import APIMessage
from app.schemas.user import PasswordChangeRequest, UserResponse, UserUpdate
from app.services.users import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser) -> UserResponse:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_me(payload: UserUpdate, session: DBSession, current_user: CurrentUser) -> UserResponse:
    return UserService(session).update_profile(current_user, payload)


@router.post("/me/avatar", response_model=UserResponse)
async def update_avatar(
    session: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
) -> UserResponse:
    return await UserService(session).update_avatar(current_user, file)


@router.post("/me/password", response_model=APIMessage)
def change_password(payload: PasswordChangeRequest, session: DBSession, current_user: CurrentUser) -> APIMessage:
    UserService(session).change_password(current_user, payload)
    return APIMessage(detail="Пароль обновлен. Войдите заново на всех устройствах")


@router.delete("/me", response_model=APIMessage)
def delete_me(session: DBSession, current_user: CurrentUser) -> APIMessage:
    UserService(session).delete_account(current_user)
    return APIMessage(detail="Аккаунт удален")
