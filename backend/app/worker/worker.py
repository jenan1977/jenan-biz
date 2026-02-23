"""
worker.py - PostgreSQL-based job worker using SKIP LOCKED.

Run with:
    python -m app.worker.worker

The worker polls the ``jobs`` table for QUEUED rows with run_at <= now(),
claims them with SELECT ... FOR UPDATE SKIP LOCKED, and dispatches them to
the appropriate handler.
"""

import logging
import os
import socket
import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.constants import JobStatus, JobType
from app.core.database import get_session_factory
from app.models.job import Job
from app.worker.handlers.financial_analysis import handle_financial_analysis
from app.worker.handlers.pdf_report import handle_pdf_report
from app.worker.handlers.bulk_inventory_update import handle_bulk_inventory_update

logger = logging.getLogger(__name__)

POLL_INTERVAL: float = float(os.getenv("WORKER_POLL_INTERVAL", "2"))
WORKER_ID: str = f"{socket.gethostname()}-{os.getpid()}"

HANDLERS = {
    JobType.FINANCIAL_ANALYSIS: handle_financial_analysis,
    JobType.PDF_REPORT: handle_pdf_report,
    JobType.BULK_INVENTORY_UPDATE: handle_bulk_inventory_update,
}


def _claim_job(db: Session) -> Job | None:
    """
    Atomically claim the next available job using SKIP LOCKED.

    Returns the claimed Job row or None if no work is available.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        select(Job)
        .where(Job.status == JobStatus.QUEUED)
        .where(Job.run_at <= now)
        .order_by(Job.priority.asc(), Job.run_at.asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = db.execute(stmt).scalars().first()
    if job is None:
        return None

    job.status = JobStatus.RUNNING
    job.locked_at = now
    job.locked_by = WORKER_ID
    job.attempts += 1
    job.updated_at = now
    db.flush()
    return job


def _requeue_or_fail(db: Session, job: Job, error: str) -> None:
    """Mark job FAILED or requeue with exponential back-off."""
    now = datetime.now(timezone.utc)
    if job.attempts >= job.max_attempts:
        job.status = JobStatus.FAILED
        job.error = error
        logger.error("Job %s permanently failed: %s", job.id, error)
    else:
        delay = 2 ** job.attempts  # exponential back-off: 2, 4, 8 … seconds
        job.status = JobStatus.QUEUED
        job.run_at = now + timedelta(seconds=delay)
        job.locked_at = None
        job.locked_by = None
        logger.warning(
            "Job %s attempt %d/%d failed; retrying in %ds",
            job.id,
            job.attempts,
            job.max_attempts,
            delay,
        )
    job.updated_at = now
    db.flush()


def process_one(db: Session) -> bool:
    """
    Claim and execute one job.

    Returns True when a job was processed, False when the queue was empty.
    """
    # Claim phase: its own committed transaction so the lock is released promptly
    with db.begin():
        job = _claim_job(db)
        if job is None:
            return False

    handler = HANDLERS.get(job.job_type)
    if handler is None:
        with db.begin():
            _requeue_or_fail(db, job, f"No handler for job type {job.job_type!r}")
        return True

    try:
        result = handler(db, job)
        with db.begin():
            job.status = JobStatus.SUCCEEDED
            job.result = result
            job.updated_at = datetime.now(timezone.utc)
        logger.info("Job %s SUCCEEDED", job.id)
    except Exception as exc:
        # Use a fresh session after rollback to persist failure state
        SessionFactory = get_session_factory()
        fresh_db: Session = SessionFactory()
        try:
            with fresh_db.begin():
                fresh_db.execute(
                    update(Job)
                    .where(Job.id == job.id)
                    .values(
                        status=JobStatus.QUEUED
                        if job.attempts < job.max_attempts
                        else JobStatus.FAILED,
                        error=str(exc),
                        run_at=datetime.now(timezone.utc)
                        + timedelta(seconds=2 ** job.attempts),
                        locked_at=None,
                        locked_by=None,
                        updated_at=datetime.now(timezone.utc),
                    )
                )
        finally:
            fresh_db.close()
        logger.exception("Job %s failed: %s", job.id, exc)

    return True


def run_worker() -> None:
    """Main worker loop. Runs until the process is killed."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Worker %s starting (poll_interval=%.1fs)", WORKER_ID, POLL_INTERVAL)

    SessionFactory = get_session_factory()
    while True:
        db: Session = SessionFactory()
        try:
            worked = process_one(db)
        except Exception:
            logger.exception("Unexpected error in worker loop")
            try:
                db.rollback()
            except Exception:
                pass
            time.sleep(POLL_INTERVAL)
        else:
            if not worked:
                time.sleep(POLL_INTERVAL)
        finally:
            db.close()


if __name__ == "__main__":
    run_worker()
