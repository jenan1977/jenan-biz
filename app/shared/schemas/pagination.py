"""Pagination schemas."""

from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    size: int = Field(default=20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response envelope."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(cls, items: List[T], total: int, params: PaginationParams) -> "PaginatedResponse[T]":
        pages = max(1, -(-total // params.size))  # ceiling division
        return cls(items=items, total=total, page=params.page, size=params.size, pages=pages)
