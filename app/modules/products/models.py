"""Product and category models."""

import uuid
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import String, Text, Boolean, Numeric, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.shared.models.base_model import BaseModel


class ProductStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"


class Category(BaseModel):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    products: Mapped[List["Product"]] = relationship("Product", back_populates="category")


class Product(BaseModel):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True
    )
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    unit: Mapped[str] = mapped_column(String(20), default="piece")
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_stock_level: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[ProductStatus] = mapped_column(
        SAEnum(ProductStatus), default=ProductStatus.ACTIVE
    )
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True)

    category: Mapped[Optional[Category]] = relationship("Category", back_populates="products")

    def __repr__(self) -> str:
        return f"<Product {self.name}>"
