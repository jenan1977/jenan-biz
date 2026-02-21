from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StockOut(BaseModel):
    id: int
    product_id: int
    current_quantity: float
    last_updated: datetime

    class Config:
        from_attributes = True


class StockWithProduct(BaseModel):
    id: int
    product_id: int
    current_quantity: float
    last_updated: datetime
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    min_stock: Optional[float] = None

    class Config:
        from_attributes = True


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    movement_type: str
    quantity: float
    reference_type: Optional[str]
    reference_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StockAdjustment(BaseModel):
    product_id: int
    quantity: float
    notes: Optional[str] = None
