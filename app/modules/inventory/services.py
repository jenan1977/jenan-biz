"""Inventory service."""

import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models import StockMovement, MovementType
from app.modules.inventory.schemas import StockMovementCreate, StockAdjustment
from app.modules.products.models import Product
from app.shared.exceptions.custom_exceptions import NotFoundException, InsufficientStockException


class InventoryService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_product(self, product_id: uuid.UUID) -> Product:
        res = await self.db.execute(
            select(Product).where(Product.id == product_id, Product.deleted_at.is_(None))
        )
        product = res.scalar_one_or_none()
        if not product:
            raise NotFoundException("Product not found.")
        return product

    async def record_movement(self, data: StockMovementCreate) -> StockMovement:
        product = await self._get_product(data.product_id)

        if data.movement_type in (MovementType.SALE, MovementType.DAMAGE):
            if product.stock_quantity < data.quantity:
                raise InsufficientStockException(
                    f"Only {product.stock_quantity} units available."
                )
            product.stock_quantity -= data.quantity
        elif data.movement_type in (MovementType.PURCHASE, MovementType.RETURN):
            product.stock_quantity += data.quantity

        movement = StockMovement(**data.model_dump())
        self.db.add(movement)
        await self.db.flush()
        return movement

    async def adjust_stock(self, data: StockAdjustment) -> StockMovement:
        product = await self._get_product(data.product_id)
        diff = data.new_quantity - product.stock_quantity
        movement_data = StockMovementCreate(
            product_id=data.product_id,
            company_id=data.company_id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=abs(diff),
            notes=data.notes,
        )
        product.stock_quantity = data.new_quantity
        movement = StockMovement(**movement_data.model_dump())
        self.db.add(movement)
        await self.db.flush()
        return movement

    async def get_movements(self, product_id: uuid.UUID) -> List[StockMovement]:
        res = await self.db.execute(
            select(StockMovement)
            .where(StockMovement.product_id == product_id)
            .order_by(StockMovement.created_at.desc())
        )
        return list(res.scalars().all())
