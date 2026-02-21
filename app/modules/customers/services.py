"""Customers service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.customers.models import Customer
from app.modules.customers.schemas import CustomerCreate, CustomerUpdate
from app.shared.exceptions.custom_exceptions import NotFoundException


class CustomersService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())
        self.db.add(customer)
        await self.db.flush()
        return customer

    async def get(self, customer_id: uuid.UUID) -> Customer:
        res = await self.db.execute(
            select(Customer).where(Customer.id == customer_id, Customer.deleted_at.is_(None))
        )
        customer = res.scalar_one_or_none()
        if not customer:
            raise NotFoundException("Customer not found.")
        return customer

    async def list_by_company(self, company_id: uuid.UUID) -> List[Customer]:
        res = await self.db.execute(
            select(Customer).where(
                Customer.company_id == company_id,
                Customer.deleted_at.is_(None),
            ).order_by(Customer.name)
        )
        return list(res.scalars().all())

    async def update(self, customer_id: uuid.UUID, data: CustomerUpdate) -> Customer:
        customer = await self.get(customer_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, field, value)
        await self.db.flush()
        return customer

    async def delete(self, customer_id: uuid.UUID) -> None:
        customer = await self.get(customer_id)
        customer.soft_delete()
        await self.db.flush()
