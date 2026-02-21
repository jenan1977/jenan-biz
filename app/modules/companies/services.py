"""Companies service."""

import uuid
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.company import Company
from app.shared.exceptions.custom_exceptions import NotFoundException, AlreadyExistsException
from app.modules.companies.schemas import CompanyCreate, CompanyUpdate


class CompaniesService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: CompanyCreate) -> Company:
        if data.tax_number:
            res = await self.db.execute(
                select(Company).where(Company.tax_number == data.tax_number)
            )
            if res.scalar_one_or_none():
                raise AlreadyExistsException("A company with this tax number already exists.")

        company = Company(**data.model_dump())
        self.db.add(company)
        await self.db.flush()
        return company

    async def get(self, company_id: uuid.UUID) -> Company:
        result = await self.db.execute(
            select(Company).where(Company.id == company_id, Company.deleted_at.is_(None))
        )
        company = result.scalar_one_or_none()
        if not company:
            raise NotFoundException("Company not found.")
        return company

    async def list_all(self) -> List[Company]:
        result = await self.db.execute(
            select(Company).where(Company.deleted_at.is_(None)).order_by(Company.name)
        )
        return list(result.scalars().all())

    async def update(self, company_id: uuid.UUID, data: CompanyUpdate) -> Company:
        company = await self.get(company_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        await self.db.flush()
        return company

    async def delete(self, company_id: uuid.UUID) -> None:
        company = await self.get(company_id)
        company.soft_delete()
        await self.db.flush()
