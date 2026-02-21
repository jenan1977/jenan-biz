"""Sales trend analysis."""

import uuid
from typing import List, Dict, Any

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models import Invoice, InvoiceItem, InvoiceStatus
from app.modules.products.models import Product


async def get_top_products(
    db: AsyncSession,
    company_id: uuid.UUID,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Return top-selling products by revenue."""
    result = await db.execute(
        select(
            InvoiceItem.product_id,
            func.sum(InvoiceItem.total).label("revenue"),
            func.sum(InvoiceItem.quantity).label("quantity_sold"),
        )
        .join(Invoice, Invoice.id == InvoiceItem.invoice_id)
        .where(
            Invoice.company_id == company_id,
            Invoice.deleted_at.is_(None),
            Invoice.status != InvoiceStatus.CANCELLED,
        )
        .group_by(InvoiceItem.product_id)
        .order_by(func.sum(InvoiceItem.total).desc())
        .limit(limit)
    )
    return [
        {
            "product_id": str(row.product_id),
            "revenue": float(row.revenue or 0),
            "quantity_sold": int(row.quantity_sold or 0),
        }
        for row in result.all()
    ]
