"""Category management service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Category
from app.modules.products.schemas import CategoryCreate
from app.shared.exceptions.custom_exceptions import NotFoundException


class CategoriesService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: CategoryCreate) -> Category:
        category = Category(**data.model_dump())
        self.db.add(category)
        await self.db.flush()
        return category

    async def get(self, category_id: uuid.UUID) -> Category:
        res = await self.db.execute(
            select(Category).where(Category.id == category_id, Category.deleted_at.is_(None))
        )
        category = res.scalar_one_or_none()
        if not category:
            raise NotFoundException("Category not found.")
        return category

    async def list_by_company(self, company_id: uuid.UUID) -> List[Category]:
        res = await self.db.execute(
            select(Category).where(
                Category.company_id == company_id,
                Category.deleted_at.is_(None),
            ).order_by(Category.name)
        )
        return list(res.scalars().all())

    async def delete(self, category_id: uuid.UUID) -> None:
        category = await self.get(category_id)
        category.soft_delete()
        await self.db.flush()
