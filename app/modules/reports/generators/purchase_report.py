"""Purchase report generator."""

import uuid
from datetime import date
from typing import Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.purchases.models import Purchase, PurchaseStatus


async def generate_purchase_report(
    db: AsyncSession,
    company_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> Dict[str, Any]:
    result = await db.execute(
        select(
            func.count(Purchase.id).label("purchase_count"),
            func.sum(Purchase.total).label("grand_total"),
            func.sum(Purchase.vat_amount).label("total_vat"),
        ).where(
            and_(
                Purchase.company_id == company_id,
                Purchase.deleted_at.is_(None),
                Purchase.status != PurchaseStatus.CANCELLED,
                func.date(Purchase.created_at) >= date_from,
                func.date(Purchase.created_at) <= date_to,
            )
        )
    )
    row = result.one()
    return {
        "date_from": str(date_from),
        "date_to": str(date_to),
        "purchase_count": row.purchase_count or 0,
        "grand_total": float(row.grand_total or 0),
        "total_vat": float(row.total_vat or 0),
    }
