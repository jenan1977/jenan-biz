"""Reports orchestration service."""

import uuid
from datetime import date
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reports.generators import (
    sales_report, purchase_report, profit_report, inventory_report, tax_report
)


class ReportsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def sales(self, company_id: uuid.UUID, date_from: date, date_to: date) -> Dict[str, Any]:
        return await sales_report.generate_sales_report(self.db, company_id, date_from, date_to)

    async def purchases(self, company_id: uuid.UUID, date_from: date, date_to: date) -> Dict[str, Any]:
        return await purchase_report.generate_purchase_report(self.db, company_id, date_from, date_to)

    async def profit(self, company_id: uuid.UUID, date_from: date, date_to: date) -> Dict[str, Any]:
        return await profit_report.generate_profit_report(self.db, company_id, date_from, date_to)

    async def inventory(self, company_id: uuid.UUID) -> Dict[str, Any]:
        return await inventory_report.generate_inventory_report(self.db, company_id)

    async def tax(self, company_id: uuid.UUID, date_from: date, date_to: date) -> Dict[str, Any]:
        return await tax_report.generate_tax_report(self.db, company_id, date_from, date_to)
