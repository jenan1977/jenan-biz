"""Shared schemas init."""
from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.shared.schemas.pagination import PaginationParams, PaginatedResponse

__all__ = ["BaseSchema", "BaseResponseSchema", "PaginationParams", "PaginatedResponse"]
