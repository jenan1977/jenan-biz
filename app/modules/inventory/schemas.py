"""Inventory schemas."""

import uuid
from decimal import Decimal
from typing import Optional

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.modules.inventory.models import MovementType


class StockMovementCreate(BaseSchema):
    product_id: uuid.UUID
    company_id: uuid.UUID
    movement_type: MovementType
    quantity: int
    unit_cost: Decimal = Decimal("0.00")
    reference_id: Optional[str] = None
    notes: Optional[str] = None


class StockMovementResponse(BaseResponseSchema):
    product_id: uuid.UUID
    company_id: uuid.UUID
    movement_type: MovementType
    quantity: int
    unit_cost: Decimal
    reference_id: Optional[str]
    notes: Optional[str]


class StockAdjustment(BaseSchema):
    product_id: uuid.UUID
    company_id: uuid.UUID
    new_quantity: int
    notes: Optional[str] = None
