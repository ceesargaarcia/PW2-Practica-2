"""User repository — all DB access for the User model lives here."""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from models.user import User, UserRole
from core.security import hash_password


class UserRepository:
    def __init__(self, db: Session):
        self._db = db

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self._db.query(User).filter(User.email == email.lower()).first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self._db.query(User).filter(User.username == username).first()
        )

    def get_all(self) -> list[User]:
        return (
            self._db.query(User).order_by(User.created_at.desc()).all()
        )

    # ── Commands ──────────────────────────────────────────────────────────────

    def create(
        self,
        username: str,
        email: str,
        plain_password: str,
        role: UserRole = UserRole.user,
    ) -> User:
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email.lower(),
            password=hash_password(plain_password),
            role=role,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def update_role(self, user: User, new_role: UserRole) -> User:
        user.role = new_role
        self._db.commit()
        self._db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self._db.delete(user)
        self._db.commit()
