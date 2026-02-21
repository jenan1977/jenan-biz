"""Profit & loss report generator."""

import uuid
from datetime import date
from typing import Dict, Any

from app.modules.reports.generators.sales_report import generate_sales_report
from app.modules.reports.generators.purchase_report import generate_purchase_report
from sqlalchemy.ext.asyncio import AsyncSession


async def generate_profit_report(
    db: AsyncSession,
    company_id: uuid.UUID,
    date_from: date,
    date_to: date,
) -> Dict[str, Any]:
    sales = await generate_sales_report(db, company_id, date_from, date_to)
    purchases = await generate_purchase_report(db, company_id, date_from, date_to)
    gross_profit = sales["grand_total"] - purchases["grand_total"]
    margin = (gross_profit / sales["grand_total"] * 100) if sales["grand_total"] else 0
    return {
        "date_from": str(date_from),
        "date_to": str(date_to),
        "total_sales": sales["grand_total"],
        "total_purchases": purchases["grand_total"],
        "gross_profit": gross_profit,
        "profit_margin_percent": round(margin, 2),
    }
