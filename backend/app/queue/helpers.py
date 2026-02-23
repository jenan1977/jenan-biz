"""
helpers.py - Low-level queue operations using SELECT … FOR UPDATE SKIP LOCKED.
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus, JobType


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def enqueue(
    db: Session,
    job_type: JobType,
    payload: Optional[Dict[str, Any]] = None,
    *,
    created_by: Optional[str] = None,
    max_attempts: int = 3,
) -> Job:
    """
    Create a new job and persist it to the database.

    Parameters
    ----------
    db:
        Active SQLAlchemy session.
    job_type:
        The handler type to invoke.
    payload:
        Arbitrary JSON-serialisable data passed to the handler.
    created_by:
        User identifier (JWT sub claim) for audit purposes.
    max_attempts:
        Maximum number of processing attempts before the job is permanently failed.

    Returns
    -------
    Job
        The newly created, uncommitted ``Job`` instance.
        The caller is responsible for ``db.commit()``.
    """
    job = Job(
        job_type=job_type,
        status=JobStatus.PENDING,
        payload=payload or {},
        max_attempts=max_attempts,
        created_by=created_by,
        run_after=_utcnow(),
    )
    db.add(job)
    db.flush()  # populate job.id without committing
    return job


def dequeue(db: Session) -> Optional[Job]:
    """
    Claim the next available pending job using ``SELECT … FOR UPDATE SKIP LOCKED``.

    A job is eligible when:
    - ``status = 'pending'``
    - ``run_after <= now()``
    - ``attempts < max_attempts``

    The claimed job is updated to ``status = 'running'`` and ``attempts`` is
    incremented.  The caller **must** commit the session after processing.

    Returns
    -------
    Job | None
        The claimed job, or ``None`` when the queue is empty.
    """
    now = _utcnow()
    job = (
        db.query(Job)
        .filter(
            Job.status == JobStatus.PENDING,
            Job.run_after <= now,
            Job.attempts < Job.max_attempts,
        )
        .order_by(Job.created_at)
        .with_for_update(skip_locked=True)
        .first()
    )

    if job is None:
        return None

    job.status = JobStatus.RUNNING
    job.attempts += 1
    job.started_at = now
    db.flush()
    return job


def mark_succeeded(db: Session, job: Job, result: Optional[Dict[str, Any]] = None) -> Job:
    """
    Mark a running job as succeeded and persist its result.

    Parameters
    ----------
    db:
        Active SQLAlchemy session (same one used to dequeue the job).
    job:
        The job returned by :func:`dequeue`.
    result:
        JSON-serialisable result data to store in ``job.result``.

    Returns
    -------
    Job
        The updated job instance.
    """
    job.status = JobStatus.SUCCEEDED
    job.result = result or {}
    job.finished_at = _utcnow()
    db.flush()
    return job


def mark_failed(
    db: Session,
    job: Job,
    error: str,
    *,
    base_delay_seconds: int = 60,
) -> Job:
    """
    Mark a running job as failed and apply exponential back-off.

    If ``job.attempts < job.max_attempts`` the job is returned to
    ``PENDING`` status with ``run_after`` set to::

        now + base_delay_seconds * 2 ^ (attempts - 1)

    If ``job.attempts >= job.max_attempts`` the job is permanently
    set to ``FAILED``.

    Parameters
    ----------
    db:
        Active SQLAlchemy session.
    job:
        The job returned by :func:`dequeue`.
    error:
        Human-readable error message.
    base_delay_seconds:
        Base delay for the first retry (default 60 s).

    Returns
    -------
    Job
        The updated job instance.
    """
    job.error = error
    now = _utcnow()

    if job.attempts < job.max_attempts:
        delay = base_delay_seconds * int(math.pow(2, job.attempts - 1))
        job.status = JobStatus.PENDING
        job.run_after = now + timedelta(seconds=delay)
    else:
        job.status = JobStatus.FAILED
        job.finished_at = now

    db.flush()
    return job
