"""
schemas/purchase_invoice.py - Purchase invoice request/response schemas.

Client MUST NOT provide: subtotal, tax_amount, total_amount, remaining_amount,
received_quantity.  All totals and receipt tracking are server-side.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, model_validator

from app.core.constants import PaymentStatus, PurchaseInvoiceStatus, ReceiptStatus, TAX_RATE


# ------------------------------------------------------------------
# Line item schemas
# ------------------------------------------------------------------


class PurchaseLineItemCreate(BaseModel):
    product_id: UUID
    ordered_quantity: Decimal
    unit_price: Decimal
    notes: Optional[str] = None

    @field_validator("ordered_quantity", mode="before")
    @classmethod
    def qty_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("ordered_quantity must be > 0")
        return v

    @field_validator("unit_price", mode="before")
    @classmethod
    def price_non_negative(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("unit_price must be >= 0")
        return v


class ReceiptLineItem(BaseModel):
    """Single line entry when recording a goods receipt."""

    product_id: UUID
    received_quantity: Decimal

    @field_validator("received_quantity", mode="before")
    @classmethod
    def qty_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("received_quantity must be > 0")
        return v


class PurchaseLineItemRead(BaseModel):
    id: UUID
    product_id: UUID
    ordered_quantity: Decimal
    received_quantity: Decimal
    unit_price: Decimal
    line_total: Decimal
    notes: Optional[str]

    model_config = {"from_attributes": True}


# ------------------------------------------------------------------
# Invoice schemas
# ------------------------------------------------------------------


class PurchaseInvoiceCreate(BaseModel):
    supplier_id: UUID
    invoice_date: datetime
    due_date: Optional[datetime] = None
    discount_amount: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal(str(TAX_RATE))
    notes: Optional[str] = None
    line_items: List[PurchaseLineItemCreate]

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
    def require_line_items(self) -> "PurchaseInvoiceCreate":
        if not self.line_items:
            raise ValueError("At least one line item is required")
        return self


class PurchaseInvoiceUpdate(BaseModel):
    """Only allowed for DRAFT invoices."""

    supplier_id: Optional[UUID] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    discount_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    notes: Optional[str] = None
    line_items: Optional[List[PurchaseLineItemCreate]] = None

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


class ReceiptCreate(BaseModel):
    """Payload for recording a goods receipt against a purchase invoice."""

    lines: List[ReceiptLineItem]

    @model_validator(mode="after")
    def require_lines(self) -> "ReceiptCreate":
        if not self.lines:
            raise ValueError("At least one receipt line is required")
        return self


class PaymentCreate(BaseModel):
    amount: Decimal

    @field_validator("amount", mode="before")
    @classmethod
    def amount_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Payment amount must be > 0")
        return v


class PurchaseInvoiceRead(BaseModel):
    id: UUID
    company_id: UUID
    supplier_id: UUID
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
    received_quantity: Decimal
    status: PurchaseInvoiceStatus
    payment_status: PaymentStatus
    receipt_status: ReceiptStatus
    notes: Optional[str]
    is_active: bool
    line_items: List[PurchaseLineItemRead]

    model_config = {"from_attributes": True}
