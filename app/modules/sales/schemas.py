"""Sales schemas."""

import uuid
from decimal import Decimal
from typing import Optional, List

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.modules.sales.models import InvoiceStatus


class InvoiceItemCreate(BaseSchema):
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0.00")
    vat_rate: Decimal = Decimal("15.00")


class InvoiceItemResponse(BaseResponseSchema):
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal
    vat_rate: Decimal
    subtotal: Decimal
    vat_amount: Decimal
    total: Decimal


class InvoiceCreate(BaseSchema):
    company_id: uuid.UUID
    customer_id: Optional[uuid.UUID] = None
    items: List[InvoiceItemCreate]
    notes: Optional[str] = None


class InvoiceResponse(BaseResponseSchema):
    company_id: uuid.UUID
    customer_id: Optional[uuid.UUID]
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    discount_amount: Decimal
    vat_amount: Decimal
    total: Decimal
    amount_paid: Decimal
    notes: Optional[str]
    items: List[InvoiceItemResponse]
