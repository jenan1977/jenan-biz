"""Suppliers schemas."""

import uuid
from decimal import Decimal
from typing import Optional
from pydantic import EmailStr

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema


class SupplierCreate(BaseSchema):
    company_id: uuid.UUID
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    notes: Optional[str] = None


class SupplierUpdate(BaseSchema):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class SupplierResponse(BaseResponseSchema):
    company_id: uuid.UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    tax_number: Optional[str]
    balance: Decimal
    is_active: bool
    notes: Optional[str]
