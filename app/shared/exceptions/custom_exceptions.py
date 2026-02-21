"""Custom application exceptions."""

from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""

    status_code: int = 500
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: Optional[str] = None, **kwargs: Any) -> None:
        self.detail = detail or self.__class__.detail
        self.extra = kwargs
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Resource not found."""
    status_code = 404
    detail = "Resource not found."


class AlreadyExistsException(AppException):
    """Resource already exists."""
    status_code = 409
    detail = "Resource already exists."


class UnauthorizedException(AppException):
    """Authentication required."""
    status_code = 401
    detail = "Authentication required."


class ForbiddenException(AppException):
    """Insufficient permissions."""
    status_code = 403
    detail = "You do not have permission to perform this action."


class ValidationException(AppException):
    """Request validation failed."""
    status_code = 422
    detail = "Validation error."


class InsufficientStockException(AppException):
    """Not enough inventory for the requested operation."""
    status_code = 400
    detail = "Insufficient stock."


class PaymentException(AppException):
    """Payment processing error."""
    status_code = 402
    detail = "Payment processing failed."


class BusinessRuleException(AppException):
    """A business rule was violated."""
    status_code = 400
    detail = "Business rule violation."
