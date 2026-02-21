"""Low-stock alert helpers."""

import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product


async def get_low_stock_alerts(db: AsyncSession, company_id: uuid.UUID) -> List[Product]:
    """Return products that are at or below their minimum stock level."""
    res = await db.execute(
        select(Product).where(
            Product.company_id == company_id,
            Product.deleted_at.is_(None),
            Product.stock_quantity <= Product.min_stock_level,
        )
    )
    return list(res.scalars().all())
