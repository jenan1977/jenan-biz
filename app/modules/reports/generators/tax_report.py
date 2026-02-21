"""VAT/Tax report generator."""

import uuid
from datetime import date
from typing import Dict, Any

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models import Invoice, InvoiceStatus
from app.modules.purchases.models import Purchase, PurchaseStatus


async def generate_tax_report(
    db: AsyncSession,
    company_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> Dict[str, Any]:
    sales_res = await db.execute(
        select(func.sum(Invoice.vat_amount)).where(
            and_(
                Invoice.company_id == company_id,
                Invoice.deleted_at.is_(None),
                Invoice.status != InvoiceStatus.CANCELLED,
                func.date(Invoice.created_at) >= date_from,
                func.date(Invoice.created_at) <= date_to,
            )
        )
    )
    output_vat = float(sales_res.scalar_one() or 0)

    purchase_res = await db.execute(
        select(func.sum(Purchase.vat_amount)).where(
            and_(
                Purchase.company_id == company_id,
                Purchase.deleted_at.is_(None),
                Purchase.status != PurchaseStatus.CANCELLED,
                func.date(Purchase.created_at) >= date_from,
                func.date(Purchase.created_at) <= date_to,
            )
        )
    )
    input_vat = float(purchase_res.scalar_one() or 0)
    net_vat = output_vat - input_vat

    return {
        "date_from": str(date_from),
        "date_to": str(date_to),
        "output_vat": output_vat,
        "input_vat": input_vat,
        "net_vat_payable": net_vat,
    }
