"""Taxes service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.taxes.models import TaxRate
from app.shared.exceptions.custom_exceptions import NotFoundException


class TaxesService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_rates(self, company_id: uuid.UUID) -> List[TaxRate]:
        res = await self.db.execute(
            select(TaxRate).where(TaxRate.company_id == company_id, TaxRate.is_active == True)
        )
        return list(res.scalars().all())

    async def create_rate(self, company_id: uuid.UUID, name: str, rate: float, is_default: bool = False) -> TaxRate:
        tax_rate = TaxRate(company_id=company_id, name=name, rate=rate, is_default=is_default)
        self.db.add(tax_rate)
        await self.db.flush()
        return tax_rate
