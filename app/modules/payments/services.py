"""Payments service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.payments.models import Payment, PaymentStatus
from app.modules.payments.schemas import PaymentCreate
from app.modules.sales.services import SalesService
from app.shared.exceptions.custom_exceptions import NotFoundException


class PaymentsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: PaymentCreate) -> Payment:
        payment = Payment(**data.model_dump(), status=PaymentStatus.COMPLETED)
        self.db.add(payment)
        await self.db.flush()

        # Update invoice paid status
        if data.invoice_id:
            sales_service = SalesService(self.db)
            await sales_service.mark_paid(data.invoice_id, data.amount)

        return payment

    async def get(self, payment_id: uuid.UUID) -> Payment:
        res = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = res.scalar_one_or_none()
        if not payment:
            raise NotFoundException("Payment not found.")
        return payment

    async def list_by_company(self, company_id: uuid.UUID) -> List[Payment]:
        res = await self.db.execute(
            select(Payment).where(Payment.company_id == company_id).order_by(Payment.created_at.desc())
        )
        return list(res.scalars().all())
