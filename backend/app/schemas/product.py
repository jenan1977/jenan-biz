"""
schemas/product.py - Product request/response schemas.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    unit_price: Decimal
    cost_price: Optional[Decimal] = None
    category: Optional[str] = None

    @field_validator("unit_price", "cost_price", mode="before")
    @classmethod
    def non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("Price must be non-negative")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    unit_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("unit_price", "cost_price", mode="before")
    @classmethod
    def non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("Price must be non-negative")
        return v


class ProductRead(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    description: Optional[str]
    sku: Optional[str]
    barcode: Optional[str]
    unit_price: Decimal
    cost_price: Optional[Decimal]
    category: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
