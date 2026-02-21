"""Suppliers service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.suppliers.models import Supplier
from app.modules.suppliers.schemas import SupplierCreate, SupplierUpdate
from app.shared.exceptions.custom_exceptions import NotFoundException


class SuppliersService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: SupplierCreate) -> Supplier:
        supplier = Supplier(**data.model_dump())
        self.db.add(supplier)
        await self.db.flush()
        return supplier

    async def get(self, supplier_id: uuid.UUID) -> Supplier:
        res = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id, Supplier.deleted_at.is_(None))
        )
        supplier = res.scalar_one_or_none()
        if not supplier:
            raise NotFoundException("Supplier not found.")
        return supplier

    async def list_by_company(self, company_id: uuid.UUID) -> List[Supplier]:
        res = await self.db.execute(
            select(Supplier).where(
                Supplier.company_id == company_id,
                Supplier.deleted_at.is_(None),
            ).order_by(Supplier.name)
        )
        return list(res.scalars().all())

    async def update(self, supplier_id: uuid.UUID, data: SupplierUpdate) -> Supplier:
        supplier = await self.get(supplier_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(supplier, field, value)
        await self.db.flush()
        return supplier

    async def delete(self, supplier_id: uuid.UUID) -> None:
        supplier = await self.get(supplier_id)
        supplier.soft_delete()
        await self.db.flush()
