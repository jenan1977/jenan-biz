"""
job.py - PostgreSQL-backed job queue model.
"""

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Enum, Index, Integer, String, Text
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import _utcnow


class JobStatus(str, enum.Enum):
    """Lifecycle states for a queued job."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class JobType(str, enum.Enum):
    """Supported job handler types."""

    FINANCIAL_ANALYSIS = "financial_analysis"
    PDF_REPORT = "pdf_report"
    BULK_INVENTORY_UPDATE = "bulk_inventory_update"


class Job(Base):
    """
    A row in the PostgreSQL job queue.

    Workers claim rows using ``SELECT … FOR UPDATE SKIP LOCKED`` so that
    multiple worker processes can run safely in parallel.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_status_created", "status", "created_at"),
        Index("ix_jobs_type", "job_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID primary key",
    )

    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="job_type"),
        nullable=False,
        comment="Determines which handler processes this job",
    )

    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"),
        nullable=False,
        default=JobStatus.PENDING,
        comment="Current lifecycle state",
    )

    payload: Mapped[Optional[Any]] = mapped_column(
        JSON().with_variant(
            __import__("sqlalchemy.dialects.postgresql", fromlist=["JSONB"]).JSONB,
            "postgresql",
        ),
        nullable=True,
        comment="Input parameters for the job handler (JSON)",
    )

    result: Mapped[Optional[Any]] = mapped_column(
        JSON().with_variant(
            __import__("sqlalchemy.dialects.postgresql", fromlist=["JSONB"]).JSONB,
            "postgresql",
        ),
        nullable=True,
        comment="Output / result data written by the handler",
    )

    error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message when status=failed",
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of processing attempts made so far",
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        comment="Maximum number of attempts before the job is permanently failed",
    )

    run_after: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        comment="Do not pick this job before this UTC timestamp (used for backoff)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        comment="UTC timestamp when the job was enqueued",
    )

    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp when a worker started processing",
    )

    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="UTC timestamp when processing completed (success or permanent failure)",
    )

    created_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="User identifier (sub claim from JWT) who requested the job",
    )

    def __repr__(self) -> str:
        return (
            f"<Job id={self.id} type={self.job_type} status={self.status} "
            f"attempts={self.attempts}/{self.max_attempts}>"
        )
