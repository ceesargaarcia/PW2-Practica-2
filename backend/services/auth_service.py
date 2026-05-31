"""Auth service — registration, login, and token generation."""

from sqlalchemy.orm import Session

from core.exceptions import AuthenticationError, ConflictError
from core.security import create_access_token, verify_password
from models.user import UserRole
from repositories.user_repository import UserRepository
from schemas.user import LoginResponse, RegisterResponse, UserInToken


class AuthService:
    def __init__(self, db: Session):
        self._repo = UserRepository(db)

    def register(
        self,
        username: str,
        email: str,
        plain_password: str,
    ) -> RegisterResponse:
        # Uniqueness check
        if self._repo.get_by_email(email):
            raise ConflictError("Email ya registrado")
        if self._repo.get_by_username(username):
            raise ConflictError("Nombre de usuario ya en uso")

        # Role is always 'user' on self-registration.
        # Promotion to admin is done via PUT /api/users/:id/role (admin only).
        user = self._repo.create(username, email, plain_password, UserRole.user)

        return RegisterResponse(
            message="Usuario registrado",
            user=UserInToken(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
            ),
        )

    def login(self, email: str, plain_password: str) -> LoginResponse:
        user = self._repo.get_by_email(email)
        if not user or not verify_password(plain_password, user.password):
            raise AuthenticationError("Credenciales inválidas")

        token_payload = {
            "userId": user.id,
            "username": user.username,
            "role": user.role.value,
        }
        token = create_access_token(token_payload)

        return LoginResponse(
            message="Login exitoso",
            token=token,
            user=UserInToken(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
            ),
        )
