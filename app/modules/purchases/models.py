"""Purchase order models."""

import uuid
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Text, Numeric, Integer, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.shared.models.base_model import BaseModel


class PurchaseStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    RECEIVED = "received"
    PARTIALLY_RECEIVED = "partially_received"
    CANCELLED = "cancelled"


class Purchase(BaseModel):
    __tablename__ = "purchases"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    supplier_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True)
    purchase_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    status: Mapped[PurchaseStatus] = mapped_column(SAEnum(PurchaseStatus), default=PurchaseStatus.DRAFT)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    vat_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    items: Mapped[List["PurchaseItem"]] = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(BaseModel):
    __tablename__ = "purchase_items"

    purchase_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("purchases.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    vat_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=15)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    vat_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)

    purchase: Mapped["Purchase"] = relationship("Purchase", back_populates="items")
