from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InvoiceItemCreate(BaseModel):
    product_id: int
    quantity: float
    unit_price: float


class InvoiceItemOut(InvoiceItemCreate):
    id: int
    cost_price: float
    total_price: float
    profit: float

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    customer_id: int
    invoice_number: str
    invoice_date: datetime
    apply_tax: bool = False
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    customer_id: Optional[int] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    apply_tax: Optional[bool] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class CustomerBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class InvoiceOut(BaseModel):
    id: int
    customer_id: int
    invoice_number: str
    invoice_date: datetime
    total_amount: float
    tax_amount: float
    grand_total: float
    profit_amount: float
    apply_tax: bool
    status: str
    notes: Optional[str]
    created_at: datetime
    items: List[InvoiceItemOut] = []
    customer: Optional[CustomerBasic] = None

    class Config:
        from_attributes = True
