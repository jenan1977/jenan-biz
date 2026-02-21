from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class PurchaseItemOut(PurchaseItemCreate):
    id: int
    total_price: float

    class Config:
        from_attributes = True


class PurchaseInvoiceCreate(BaseModel):
    supplier_id: int
    invoice_number: str
    invoice_date: datetime
    apply_tax: bool = False
    notes: Optional[str] = None
    items: List[PurchaseItemCreate]


class PurchaseInvoiceUpdate(BaseModel):
    supplier_id: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    apply_tax: Optional[bool] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class SupplierBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PurchaseInvoiceOut(BaseModel):
    id: int
    supplier_id: int
    invoice_number: str
    invoice_date: datetime
    total_amount: float
    tax_amount: float
    grand_total: float
    apply_tax: bool
    status: str
    notes: Optional[str]
    file_path: Optional[str]
    created_at: datetime
    items: List[PurchaseItemOut] = []
    supplier: Optional[SupplierBasic] = None

    class Config:
        from_attributes = True
