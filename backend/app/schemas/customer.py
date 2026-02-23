"""
schemas/customer.py - Customer request/response schemas.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.core.constants import CustomerType


class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    customer_type: CustomerType = CustomerType.RETAIL

    @field_validator("credit_limit", mode="before")
    @classmethod
    def non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("credit_limit must be non-negative")
        return v


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    customer_type: Optional[CustomerType] = None
    is_active: Optional[bool] = None

    @field_validator("credit_limit", mode="before")
    @classmethod
    def non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("credit_limit must be non-negative")
        return v


class CustomerRead(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    tax_id: Optional[str]
    credit_limit: Optional[Decimal]
    customer_type: CustomerType
    is_active: bool

    model_config = {"from_attributes": True}
