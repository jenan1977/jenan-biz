"""Payment schemas."""

import uuid
from decimal import Decimal
from typing import Optional

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.modules.payments.models import PaymentStatus, PaymentMethod


class PaymentCreate(BaseSchema):
    company_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    amount: Decimal
    currency: str = "SAR"
    method: PaymentMethod
    notes: Optional[str] = None


class PaymentResponse(BaseResponseSchema):
    company_id: uuid.UUID
    invoice_id: Optional[uuid.UUID]
    amount: Decimal
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    gateway_reference: Optional[str]
    notes: Optional[str]
