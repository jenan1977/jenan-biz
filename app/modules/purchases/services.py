"""Purchases service."""

import uuid
from decimal import Decimal
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.purchases.models import Purchase, PurchaseItem, PurchaseStatus
from app.modules.purchases.schemas import PurchaseCreate
from app.modules.inventory.services import InventoryService
from app.modules.inventory.schemas import StockMovementCreate
from app.modules.inventory.models import MovementType
from app.shared.utils.calculators import calculate_line_total
from app.shared.exceptions.custom_exceptions import NotFoundException


class PurchasesService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _next_purchase_number(self, company_id: uuid.UUID) -> str:
        res = await self.db.execute(
            select(func.count(Purchase.id)).where(Purchase.company_id == company_id)
        )
        count = res.scalar_one() + 1
        from app.shared.utils.helpers import generate_purchase_number
        return generate_purchase_number(count)

    async def create(self, data: PurchaseCreate) -> Purchase:
        purchase_number = await self._next_purchase_number(data.company_id)
        purchase = Purchase(
            company_id=data.company_id,
            supplier_id=data.supplier_id,
            purchase_number=purchase_number,
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
            item = PurchaseItem(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount_percent=item_data.discount_percent,
                vat_rate=item_data.vat_rate,
                subtotal=line["subtotal"],
                vat_amount=line["vat_amount"],
                total=line["total"],
            )
            purchase.items.append(item)
            total_subtotal += line["subtotal"]
            total_vat += line["vat_amount"]
            total_discount += line["discount_amount"]

        purchase.subtotal = total_subtotal
        purchase.vat_amount = total_vat
        purchase.discount_amount = total_discount
        purchase.total = total_subtotal - total_discount + total_vat

        self.db.add(purchase)
        await self.db.flush()

        # Update inventory
        inv_service = InventoryService(self.db)
        for item in purchase.items:
            await inv_service.record_movement(StockMovementCreate(
                product_id=item.product_id,
                company_id=data.company_id,
                movement_type=MovementType.PURCHASE,
                quantity=item.quantity,
                unit_cost=item.unit_price,
                reference_id=str(purchase.id),
            ))

        purchase.status = PurchaseStatus.RECEIVED
        await self.db.flush()
        return purchase

    async def get(self, purchase_id: uuid.UUID) -> Purchase:
        res = await self.db.execute(
            select(Purchase).where(Purchase.id == purchase_id, Purchase.deleted_at.is_(None))
        )
        purchase = res.scalar_one_or_none()
        if not purchase:
            raise NotFoundException("Purchase not found.")
        return purchase

    async def list_by_company(self, company_id: uuid.UUID) -> List[Purchase]:
        res = await self.db.execute(
            select(Purchase).where(
                Purchase.company_id == company_id,
                Purchase.deleted_at.is_(None),
            ).order_by(Purchase.created_at.desc())
        )
        return list(res.scalars().all())
