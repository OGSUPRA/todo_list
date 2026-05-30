from __future__ import annotations

import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User
from app.repositories.user import UserRepository
from app.schemas.user import PasswordChangeRequest, UserUpdate
from app.utils.files import save_avatar


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.users = UserRepository(session)

    def update_profile(self, user: User, payload: UserUpdate) -> User:
        existing_by_username = self.users.get_by_username(payload.username)
        if existing_by_username and existing_by_username.id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Имя пользователя уже занято")

        existing_by_email = self.users.get_by_email(payload.email)
        if existing_by_email and existing_by_email.id != user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email уже используется")

        user.username = payload.username
        user.email = payload.email
        self.session.commit()
        self.session.refresh(user)
        return user

    def change_password(self, user: User, payload: PasswordChangeRequest) -> None:
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Текущий пароль указан неверно")

        user.password_hash = hash_password(payload.new_password)
        user.token_version += 1
        self.session.commit()

    async def update_avatar(self, user: User, file: UploadFile) -> User:
        user.avatar_path = await save_avatar(file, user.id)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_account(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
