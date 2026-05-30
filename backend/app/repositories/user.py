from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: uuid.UUID | str) -> User | None:
        return self.session.get(User, user_id)

    def get_by_username_or_email(self, value: str) -> User | None:
        statement = select(User).where(or_(User.username == value, User.email == value))
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.execute(statement).scalar_one_or_none()

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        self.session.refresh(user)
        return user
