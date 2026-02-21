"""Report models (saved/scheduled reports)."""

import uuid
from typing import Optional, Any

from sqlalchemy import String, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.models.base_model import BaseModel


class SavedReport(BaseModel):
    __tablename__ = "saved_reports"

    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    schedule_cron: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
