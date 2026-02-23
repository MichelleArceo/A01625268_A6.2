"""Custom exceptions for the reservation system."""


class ValidationError(ValueError):
    """Raised when domain validation fails."""


class NotFoundError(LookupError):
    """Raised when an entity is not found."""


class ConflictError(RuntimeError):
    """Raised when an operation conflicts with current state."""


class StorageError(RuntimeError):
    """Raised when persistence layer fails unexpectedly."""
