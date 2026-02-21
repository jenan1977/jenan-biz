"""Stock movement helpers (batch processing)."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models import StockMovement
from app.modules.inventory.schemas import StockMovementCreate
from app.modules.inventory.services import InventoryService


async def process_bulk_movements(
    db: AsyncSession, movements: List[StockMovementCreate]
) -> List[StockMovement]:
    """Process a list of stock movements atomically."""
    service = InventoryService(db)
    results = []
    for movement in movements:
        result = await service.record_movement(movement)
        results.append(result)
    return results
