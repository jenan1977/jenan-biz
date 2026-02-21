"""Notification models."""

import uuid
from typing import Optional

from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum

from app.shared.models.base_model import BaseModel


class NotificationType(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType), default=NotificationType.INFO)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
