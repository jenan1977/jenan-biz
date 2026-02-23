"""
job.py - Background job queue model (PostgreSQL-based, SKIP LOCKED).
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, Enum, Index, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import JobStatus, JobType
from app.core.database import Base
from app.models.base import _utcnow


class Job(Base):
    """
    A durable background job stored in PostgreSQL.

    Workers claim rows using SELECT ... FOR UPDATE SKIP LOCKED to ensure
    exactly-once processing across multiple worker processes.
    """

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_status_run_at_priority", "status", "run_at", "priority"),
        Index("ix_jobs_company_id", "company_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID primary key",
    )
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
        comment="Owning company; NULL for global jobs",
    )
    job_type: Mapped[JobType] = mapped_column(
        Enum(JobType, name="job_type"),
        nullable=False,
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"),
        nullable=False,
        default=JobStatus.QUEUED,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        comment="Lower number = higher priority",
    )
    payload: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
        comment="Job-type-specific input parameters",
    )
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        comment="Job output written on SUCCEEDED",
    )
    error: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message written on FAILED",
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    max_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
    )
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        comment="Earliest time the job may be executed",
    )
    locked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When this job was last claimed by a worker",
    )
    locked_by: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Worker identifier that holds the lock",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} type={self.job_type} status={self.status}>"
