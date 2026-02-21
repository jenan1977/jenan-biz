"""Analytics cached data models."""

import uuid
from typing import Optional, Any
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.models.base_model import BaseModel


class AnalyticsSnapshot(BaseModel):
    __tablename__ = "analytics_snapshots"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
