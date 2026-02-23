"""
schemas/supplier.py - Supplier request/response schemas.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SupplierCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    payment_terms: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierRead(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    tax_id: Optional[str]
    payment_terms: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}
