from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    invoice_date = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    profit_amount = Column(Float, default=0.0)
    apply_tax = Column(Boolean, default=False)
    status = Column(String, default="draft")  # draft, confirmed, cancelled
    notes = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Customer")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    created_by_user = relationship("User")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False, default=0.0)
    total_price = Column(Float, nullable=False)
    profit = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")
