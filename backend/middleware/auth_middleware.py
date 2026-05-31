"""FastAPI dependencies for JWT authentication and role enforcement."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.security import decode_token
from jose import JWTError

bearer_scheme = HTTPBearer(auto_error=False)


def _extract_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """Decode the Bearer token and return its payload.

    401 → no token present (frontend redirects to login).
    401 → token expired or invalid (frontend treats as session ended).

    Both cases must be 401 so the Svelte frontend's api.js error handler
    correctly redirects the user to the login page.  Returning 403 for an
    expired token would silently block the user without triggering the
    redirect, because the frontend only checks for 403 to show a
    'forbidden' message, not to clear the session.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado.",
        )
    try:
        payload = decode_token(credentials.credentials)
        return payload
    except JWTError:
        # Token inválido o expirado → 401, no 403.
        # The user needs to log in again, not just be told they lack permissions.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
        )


def get_current_user(payload: dict = Depends(_extract_token)) -> dict:
    """Dependency that returns the token payload (authenticated user)."""
    return payload


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency that additionally checks the admin role.

    Only reaches this point if the token is valid (401 already handled above).
    A valid token with insufficient role → 403.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol admin.",
        )
    return current_user
