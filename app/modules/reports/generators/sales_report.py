"""Sales report generator."""

import uuid
from datetime import date
from typing import List, Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models import Invoice, InvoiceItem, InvoiceStatus


async def generate_sales_report(
    db: AsyncSession,
    company_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> Dict[str, Any]:
    """Return sales summary for the given date range."""
    result = await db.execute(
        select(
            func.count(Invoice.id).label("invoice_count"),
            func.sum(Invoice.subtotal).label("total_subtotal"),
            func.sum(Invoice.vat_amount).label("total_vat"),
            func.sum(Invoice.total).label("grand_total"),
        ).where(
            and_(
                Invoice.company_id == company_id,
                Invoice.deleted_at.is_(None),
                Invoice.status != InvoiceStatus.CANCELLED,
                func.date(Invoice.created_at) >= date_from,
                func.date(Invoice.created_at) <= date_to,
            )
        )
    )
    row = result.one()
    return {
        "date_from": str(date_from),
        "date_to": str(date_to),
        "invoice_count": row.invoice_count or 0,
        "total_subtotal": float(row.total_subtotal or 0),
        "total_vat": float(row.total_vat or 0),
        "grand_total": float(row.grand_total or 0),
    }
