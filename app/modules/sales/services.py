"""Sales service."""

import uuid
from decimal import Decimal
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sales.models import Invoice, InvoiceItem, InvoiceStatus
from app.modules.sales.schemas import InvoiceCreate
from app.modules.inventory.services import InventoryService
from app.modules.inventory.schemas import StockMovementCreate
from app.modules.inventory.models import MovementType
from app.shared.utils.calculators import calculate_line_total
from app.shared.exceptions.custom_exceptions import NotFoundException


class SalesService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _next_invoice_number(self, company_id: uuid.UUID) -> str:
        res = await self.db.execute(
            select(func.count(Invoice.id)).where(Invoice.company_id == company_id)
        )
        count = res.scalar_one() + 1
        from app.shared.utils.helpers import generate_invoice_number
        return generate_invoice_number("INV", count)

    async def create(self, data: InvoiceCreate) -> Invoice:
        invoice_number = await self._next_invoice_number(data.company_id)
        invoice = Invoice(
            company_id=data.company_id,
            customer_id=data.customer_id,
            invoice_number=invoice_number,
            notes=data.notes,
        )

        total_subtotal = Decimal("0")
        total_vat = Decimal("0")
        total_discount = Decimal("0")

        for item_data in data.items:
            line = calculate_line_total(
                item_data.unit_price,
                item_data.quantity,
                item_data.discount_percent,
                item_data.vat_rate,
            )
            item = InvoiceItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount_percent=item_data.discount_percent,
                vat_rate=item_data.vat_rate,
                subtotal=line["subtotal"],
                vat_amount=line["vat_amount"],
                total=line["total"],
            )
            invoice.items.append(item)
            total_subtotal += line["subtotal"]
            total_vat += line["vat_amount"]
            total_discount += line["discount_amount"]

        invoice.subtotal = total_subtotal
        invoice.vat_amount = total_vat
        invoice.discount_amount = total_discount
        invoice.total = total_subtotal - total_discount + total_vat

        self.db.add(invoice)
        await self.db.flush()

        # Deduct inventory
        inv_service = InventoryService(self.db)
        for item in invoice.items:
            await inv_service.record_movement(StockMovementCreate(
                product_id=item.product_id,
                company_id=data.company_id,
                movement_type=MovementType.SALE,
                quantity=item.quantity,
                unit_cost=item.unit_price,
                reference_id=str(invoice.id),
            ))

        invoice.status = InvoiceStatus.PENDING
        await self.db.flush()
        return invoice

    async def get(self, invoice_id: uuid.UUID) -> Invoice:
        res = await self.db.execute(
            select(Invoice).where(Invoice.id == invoice_id, Invoice.deleted_at.is_(None))
        )
        invoice = res.scalar_one_or_none()
        if not invoice:
            raise NotFoundException("Invoice not found.")
        return invoice

    async def list_by_company(self, company_id: uuid.UUID) -> List[Invoice]:
        res = await self.db.execute(
            select(Invoice).where(
                Invoice.company_id == company_id,
                Invoice.deleted_at.is_(None),
            ).order_by(Invoice.created_at.desc())
        )
        return list(res.scalars().all())

    async def mark_paid(self, invoice_id: uuid.UUID, amount: Decimal) -> Invoice:
        invoice = await self.get(invoice_id)
        invoice.amount_paid += amount
        if invoice.amount_paid >= invoice.total:
            invoice.status = InvoiceStatus.PAID
        else:
            invoice.status = InvoiceStatus.PARTIALLY_PAID
        await self.db.flush()
        return invoice
