"""User service — profile and admin operations."""

from sqlalchemy.orm import Session

from core.exceptions import ForbiddenError, NotFoundError
from models.user import UserRole
from repositories.user_repository import UserRepository
from schemas.user import UserPublic


class UserService:
    def __init__(self, db: Session):
        self._repo = UserRepository(db)

    def get_all(self) -> list[UserPublic]:
        users = self._repo.get_all()
        return [UserPublic.from_orm_obj(u) for u in users]

    def get_me(self, user_id: str) -> UserPublic:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")
        return UserPublic.from_orm_obj(user)

    def update_role(self, target_id: str, new_role: UserRole) -> UserPublic:
        user = self._repo.get_by_id(target_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")
        updated = self._repo.update_role(user, new_role)
        return UserPublic.from_orm_obj(updated)

    def delete(self, target_id: str, requesting_user_id: str) -> UserPublic:
        if target_id == requesting_user_id:
            raise ForbiddenError("No puedes eliminarte a ti mismo")
        user = self._repo.get_by_id(target_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")
        snapshot = UserPublic.from_orm_obj(user)
        self._repo.delete(user)
        return snapshot
