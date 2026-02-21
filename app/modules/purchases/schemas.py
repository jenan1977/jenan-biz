"""Purchases schemas."""

import uuid
from decimal import Decimal
from typing import Optional, List

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.modules.purchases.models import PurchaseStatus


class PurchaseItemCreate(BaseSchema):
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal = Decimal("0.00")
    vat_rate: Decimal = Decimal("15.00")


class PurchaseItemResponse(BaseResponseSchema):
    product_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    discount_percent: Decimal
    vat_rate: Decimal
    subtotal: Decimal
    vat_amount: Decimal
    total: Decimal


class PurchaseCreate(BaseSchema):
    company_id: uuid.UUID
    supplier_id: Optional[uuid.UUID] = None
    items: List[PurchaseItemCreate]
    notes: Optional[str] = None


class PurchaseResponse(BaseResponseSchema):
    company_id: uuid.UUID
    supplier_id: Optional[uuid.UUID]
    purchase_number: str
    status: PurchaseStatus
    subtotal: Decimal
    discount_amount: Decimal
    vat_amount: Decimal
    total: Decimal
    notes: Optional[str]
    items: List[PurchaseItemResponse]
