from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class StockMovementBase(BaseModel):
    product_id: int
    movement_type: str
    quantity: float
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockAdjustment(BaseModel):
    product_id: int
    quantity: float
    notes: Optional[str] = None


class StockMovementResponse(StockMovementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
