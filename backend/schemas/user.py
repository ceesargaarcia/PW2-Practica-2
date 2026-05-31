from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from models.user import UserRole


# ── Request schemas ───────────────────────────────────────────────────────────

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    # role is intentionally NOT accepted from the client.
    # All self-registrations are always 'user'; admins are promoted
    # via PUT /api/users/:id/role (admin-only endpoint).


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserRoleUpdateRequest(BaseModel):
    role: UserRole


# ── Response schemas ──────────────────────────────────────────────────────────

class UserPublic(BaseModel):
    """User data safe to expose publicly (no password)."""

    id: str = Field(alias="_id")
    username: str
    email: str
    role: UserRole
    created_at: datetime = Field(alias="createdAt")

    model_config = {"populate_by_name": True, "from_attributes": True}

    @classmethod
    def from_orm_obj(cls, user) -> "UserPublic":
        return cls(
            _id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            createdAt=user.created_at,
        )


class UserInToken(BaseModel):
    """Minimal user info embedded in the JWT payload and login response."""

    id: str
    username: str
    email: str
    role: UserRole


class LoginResponse(BaseModel):
    message: str = "Login exitoso"
    token: str
    user: UserInToken


class RegisterResponse(BaseModel):
    message: str = "Usuario registrado"
    user: UserInToken
