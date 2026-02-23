"""
schemas/sales_invoice.py - Sales invoice request/response schemas.

Client MUST NOT provide: subtotal, tax_amount, total_amount, remaining_amount.
All financial totals are computed server-side.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator

from app.core.constants import InvoiceStatus, PaymentStatus, TAX_RATE


# ------------------------------------------------------------------
# Line item schemas
# ------------------------------------------------------------------


class SalesLineItemCreate(BaseModel):
    product_id: UUID
    quantity: Decimal
    unit_price: Decimal
    notes: Optional[str] = None

    @field_validator("quantity", mode="before")
    @classmethod
    def qty_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("quantity must be > 0")
        return v

    @field_validator("unit_price", mode="before")
    @classmethod
    def price_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("unit_price must be >= 0")
        return v


class SalesLineItemRead(BaseModel):
    id: UUID
    product_id: UUID
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    notes: Optional[str]

    model_config = {"from_attributes": True}


# ------------------------------------------------------------------
# Invoice schemas
# ------------------------------------------------------------------


class SalesInvoiceCreate(BaseModel):
    customer_id: UUID
    invoice_date: datetime
    due_date: Optional[datetime] = None
    discount_amount: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal(str(TAX_RATE))
    notes: Optional[str] = None
    line_items: List[SalesLineItemCreate]

    @field_validator("discount_amount", mode="before")
    @classmethod
    def discount_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("discount_amount must be >= 0")
        return v

    @field_validator("tax_rate", mode="before")
    @classmethod
    def tax_rate_valid(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("tax_rate must be >= 0")
        return v

    @model_validator(mode="after")
    def require_line_items(self) -> "SalesInvoiceCreate":
        if not self.line_items:
            raise ValueError("At least one line item is required")
        return self


class SalesInvoiceUpdate(BaseModel):
    """Only allowed for DRAFT invoices."""

    customer_id: Optional[UUID] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    line_items: Optional[List[SalesLineItemCreate]] = None

    @field_validator("discount_amount", mode="before")
    @classmethod
    def discount_non_negative(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("discount_amount must be >= 0")
        return v

    @field_validator("tax_rate", mode="before")
    @classmethod
    def tax_rate_valid(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v < 0:
            raise ValueError("tax_rate must be >= 0")
        return v


class PaymentCreate(BaseModel):
    amount: Decimal

    @field_validator("amount", mode="before")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Payment amount must be > 0")
        return v


class SalesInvoiceRead(BaseModel):
    id: UUID
    company_id: UUID
    customer_id: UUID
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime]
    tax_rate: Decimal
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    remaining_amount: Decimal
    status: InvoiceStatus
    payment_status: PaymentStatus
    notes: Optional[str]
    is_active: bool
    line_items: List[SalesLineItemRead]

    model_config = {"from_attributes": True}
