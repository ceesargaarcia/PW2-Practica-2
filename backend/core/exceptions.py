"""Domain-level exceptions.

These are raised by services/repositories and translated into HTTP responses
by the global exception handlers registered in main.py.
"""


class NotFoundError(Exception):
    """Resource not found."""

    def __init__(self, detail: str = "Recurso no encontrado"):
        self.detail = detail
        super().__init__(detail)


class ConflictError(Exception):
    """Duplicate / uniqueness violation."""

    def __init__(self, detail: str = "Conflicto de datos"):
        self.detail = detail
        super().__init__(detail)


class AuthenticationError(Exception):
    """Invalid credentials."""

    def __init__(self, detail: str = "Credenciales inválidas"):
        self.detail = detail
        super().__init__(detail)


class ForbiddenError(Exception):
    """Insufficient permissions."""

    def __init__(self, detail: str = "Acceso denegado"):
        self.detail = detail
        super().__init__(detail)
