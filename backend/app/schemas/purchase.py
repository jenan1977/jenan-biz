from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class PurchaseItemBase(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItemResponse(PurchaseItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    total_price: float


class PurchaseInvoiceBase(BaseModel):
    supplier_id: int
    date: date
    apply_tax: bool = False
    notes: Optional[str] = None
    status: str = "draft"


class PurchaseInvoiceCreate(PurchaseInvoiceBase):
    items: List[PurchaseItemCreate]


class PurchaseInvoiceUpdate(BaseModel):
    supplier_id: Optional[int] = None
    date: Optional[date] = None
    apply_tax: Optional[bool] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class PurchaseInvoiceResponse(PurchaseInvoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_number: str
    subtotal: float
    tax_amount: float
    total_amount: float
    file_url: Optional[str] = None
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    items: List[PurchaseItemResponse] = []
