"""Sales heatmap generator."""

import uuid
from typing import List, Dict, Any

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models import Invoice, InvoiceStatus


async def generate_sales_heatmap(
    db: AsyncSession,
    company_id: uuid.UUID,
    year: int,
) -> List[Dict[str, Any]]:
    """Return monthly sales totals for the heatmap."""
    result = await db.execute(
        select(
            extract("month", Invoice.created_at).label("month"),
            func.sum(Invoice.total).label("total"),
            func.count(Invoice.id).label("count"),
        ).where(
            Invoice.company_id == company_id,
            Invoice.deleted_at.is_(None),
            Invoice.status != InvoiceStatus.CANCELLED,
            extract("year", Invoice.created_at) == year,
        ).group_by("month").order_by("month")
    )
    return [
        {"month": int(row.month), "total": float(row.total or 0), "count": row.count}
        for row in result.all()
    ]
