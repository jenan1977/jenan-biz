"""Products schemas."""

import uuid
from decimal import Decimal
from typing import Optional
from pydantic import Field

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.modules.products.models import ProductStatus


class CategoryCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    company_id: uuid.UUID


class CategoryResponse(BaseResponseSchema):
    name: str
    description: Optional[str]
    parent_id: Optional[uuid.UUID]
    company_id: uuid.UUID
    is_active: bool


class ProductCreate(BaseSchema):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    company_id: uuid.UUID
    cost_price: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    unit: str = "piece"
    stock_quantity: int = 0
    min_stock_level: int = 5
    status: ProductStatus = ProductStatus.ACTIVE
    image_url: Optional[str] = None
    is_taxable: bool = True


class ProductUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    category_id: Optional[uuid.UUID] = None
    cost_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    unit: Optional[str] = None
    min_stock_level: Optional[int] = None
    status: Optional[ProductStatus] = None
    image_url: Optional[str] = None
    is_taxable: Optional[bool] = None


class ProductResponse(BaseResponseSchema):
    name: str
    description: Optional[str]
    sku: Optional[str]
    barcode: Optional[str]
    category_id: Optional[uuid.UUID]
    company_id: uuid.UUID
    cost_price: Decimal
    selling_price: Decimal
    unit: str
    stock_quantity: int
    min_stock_level: int
    status: ProductStatus
    image_url: Optional[str]
    is_taxable: bool
