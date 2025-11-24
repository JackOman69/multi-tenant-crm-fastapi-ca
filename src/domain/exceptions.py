class DomainError(Exception):
    """Base exception for all domain-level errors."""

    pass


class AuthenticationError(DomainError):
    """Raised when authentication fails."""

    pass


class AuthorizationError(DomainError):
    """Raised when user lacks permission for an operation."""

    pass


class ValidationError(DomainError):
    """Raised when input validation fails."""

    pass


class NotFoundError(DomainError):
    """Raised when a requested resource is not found."""

    pass


class ConflictError(DomainError):
    """Raised when a business rule conflict occurs."""

    pass
