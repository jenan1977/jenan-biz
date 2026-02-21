from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    purchase_price: float = 0.0
    sale_price: float = 0.0
    unit: str = "unit"
    category: Optional[str] = None
    min_stock: float = 0.0


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None


class StockInfo(BaseModel):
    current_quantity: float = 0.0

    class Config:
        from_attributes = True


class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    stock: Optional[StockInfo] = None

    class Config:
        from_attributes = True
