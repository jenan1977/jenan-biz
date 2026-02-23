"""
base.py - Abstract base model providing common columns for all ORM models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _utcnow() -> datetime:
    """Return the current time in UTC."""
    return datetime.now(timezone.utc)


class BaseModel(Base):
    """
    Abstract SQLAlchemy model with audit columns shared by all entities.

    Columns
    -------
    id          : UUID primary key (auto-generated).
    created_at  : Timestamp of record creation (UTC, set once).
    updated_at  : Timestamp of last update (UTC, updated on write).
    is_active   : Soft-disable flag; active by default.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="UUID primary key",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
        comment="UTC timestamp when the record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
        comment="UTC timestamp of the last update",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="False means the record is logically disabled",
    )
