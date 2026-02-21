"""Inventory valuation report."""

import uuid
from typing import Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product


async def generate_inventory_report(
    db: AsyncSession,
    company_id: uuid.UUID,
) -> Dict[str, Any]:
    res = await db.execute(
        select(Product).where(
            Product.company_id == company_id,
            Product.deleted_at.is_(None),
        )
    )
    products = res.scalars().all()
    items = []
    total_value = 0.0
    for p in products:
        value = float(p.cost_price) * p.stock_quantity
        total_value += value
        items.append({
            "product_id": str(p.id),
            "name": p.name,
            "sku": p.sku,
            "stock_quantity": p.stock_quantity,
            "cost_price": float(p.cost_price),
            "value": value,
        })
    return {"items": items, "total_inventory_value": total_value}
