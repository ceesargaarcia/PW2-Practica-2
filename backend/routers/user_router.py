from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db
from middleware.auth_middleware import get_current_user, require_admin
from schemas.user import UserPublic, UserRoleUpdateRequest
from services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


def _svc(db): return UserService(db)


@router.get("", response_model=list[UserPublic])
@router.get("/", response_model=list[UserPublic], include_in_schema=False)
def list_users(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return _svc(db).get_all()


@router.get("/me", response_model=UserPublic)
def get_me(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return _svc(db).get_me(current_user["userId"])


@router.put("/{user_id}/role", response_model=UserPublic)
def update_role(
    user_id: str,
    body: UserRoleUpdateRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return _svc(db).update_role(user_id, body.role)


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_admin),
):
    snapshot = _svc(db).delete(user_id, current_user["userId"])
    return {"message": "Usuario eliminado", "user": snapshot}
