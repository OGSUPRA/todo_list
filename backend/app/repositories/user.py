from __future__ import annotations

import uuid
from typing import Optional, Union

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: Union[uuid.UUID, str]) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_username_or_email(self, value: str) -> Optional[User]:
        statement = select(User).where(or_(User.username == value, User.email == value))
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.execute(statement).scalar_one_or_none()

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user
