from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class SaleItemBase(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemResponse(SaleItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    cost_price: float
    total_price: float


class SaleInvoiceBase(BaseModel):
    customer_id: int
    date: date
    apply_tax: bool = False
    notes: Optional[str] = None
    status: str = "draft"


class SaleInvoiceCreate(SaleInvoiceBase):
    items: List[SaleItemCreate]


class SaleInvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    date: Optional[date] = None
    apply_tax: Optional[bool] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class SaleInvoiceResponse(SaleInvoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    subtotal: float
    tax_amount: float
    total_amount: float
    profit: float
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    items: List[SaleItemResponse] = []
