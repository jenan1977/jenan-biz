from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    cost_price: float = 0.0
    selling_price: float = 0.0
    min_stock_level: float = 0.0
    image_url: Optional[str] = None
    category: Optional[str] = None
    unit: str = "pcs"
    is_active: bool = True


class ProductCreate(ProductBase):
    stock_quantity: float = 0.0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    stock_quantity: Optional[float] = None
    min_stock_level: Optional[float] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stock_quantity: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
