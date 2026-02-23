"""
schemas/inventory.py - Inventory request/response schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.core.constants import StockStatus


class InventoryUpdate(BaseModel):
    """Fields that can be manually updated on an inventory record."""

    reorder_level: Optional[Decimal] = None
    last_stock_check_date: Optional[datetime] = None


class InventoryRead(BaseModel):
    id: UUID
    company_id: UUID
    product_id: UUID
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal
    reorder_level: Optional[Decimal]
    last_stock_check_date: Optional[datetime]
    last_received_date: Optional[datetime]
    last_sold_date: Optional[datetime]
    stock_status: StockStatus
    is_active: bool

    model_config = {"from_attributes": True}
