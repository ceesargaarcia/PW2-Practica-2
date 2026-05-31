from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from db.database import get_db
from schemas.user import (
    LoginResponse,
    RegisterResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(body: UserRegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register(
        username=body.username,
        email=body.email,
        plain_password=body.password,
        # role is NOT passed — always forced to 'user' in the service layer
    )


@router.post("/login", response_model=LoginResponse)
def login(body: UserLoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.login(email=body.email, plain_password=body.password)


@router.post("/logout")
def logout():
    # Stateless JWT — client drops the token; server just acknowledges.
    return {"message": "Logout exitoso"}
