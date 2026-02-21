"""Analytics service."""

import uuid
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.heatmap import generate_sales_heatmap
from app.modules.analytics.trends import get_top_products


class AnalyticsService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def sales_heatmap(self, company_id: uuid.UUID, year: int) -> List[Dict[str, Any]]:
        return await generate_sales_heatmap(self.db, company_id, year)

    async def top_products(self, company_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        return await get_top_products(self.db, company_id, limit)
