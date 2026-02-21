"""Products service."""

import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product, Category
from app.modules.products.schemas import ProductCreate, ProductUpdate, CategoryCreate
from app.shared.exceptions.custom_exceptions import NotFoundException, AlreadyExistsException


class ProductsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_product(self, data: ProductCreate) -> Product:
        if data.sku:
            res = await self.db.execute(select(Product).where(Product.sku == data.sku))
            if res.scalar_one_or_none():
                raise AlreadyExistsException("Product with this SKU already exists.")
        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.flush()
        return product

    async def get_product(self, product_id: uuid.UUID) -> Product:
        res = await self.db.execute(
            select(Product).where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        product = res.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product not found.")
        return product

    async def list_products(self, company_id: uuid.UUID) -> List[Product]:
        res = await self.db.execute(
            select(Product).where(
                Product.company_id == company_id,
                Product.deleted_at.is_(None),
            ).order_by(Product.name)
        )
        return list(res.scalars().all())

    async def update_product(self, product_id: uuid.UUID, data: ProductUpdate) -> Product:
        product = await self.get_product(product_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.db.flush()
        return product

    async def delete_product(self, product_id: uuid.UUID) -> None:
        product = await self.get_product(product_id)
        product.soft_delete()
        await self.db.flush()

    async def get_low_stock_products(self, company_id: uuid.UUID) -> List[Product]:
        res = await self.db.execute(
            select(Product).where(
                Product.company_id == company_id,
                Product.deleted_at.is_(None),
                Product.stock_quantity <= Product.min_stock_level,
            )
        )
        return list(res.scalars().all())
