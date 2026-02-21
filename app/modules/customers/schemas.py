"""Customers schemas."""

import uuid
from decimal import Decimal
from typing import Optional
from pydantic import EmailStr

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema


class CustomerCreate(BaseSchema):
    company_id: uuid.UUID
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    credit_limit: Decimal = Decimal("0.00")
    notes: Optional[str] = None


class CustomerUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CustomerResponse(BaseResponseSchema):
    company_id: uuid.UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    tax_number: Optional[str]
    credit_limit: Decimal
    balance: Decimal
    is_active: bool
    notes: Optional[str]
