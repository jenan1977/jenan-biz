"""
test_queue.py - Unit tests for queue helpers (enqueue / dequeue / state transitions).

These tests use an in-memory SQLite database so no live PostgreSQL is required.
Note: SKIP LOCKED is PostgreSQL-specific; the SELECT … FOR UPDATE path is still
exercised here (SQLite ignores the SKIP LOCKED hint gracefully in SQLAlchemy).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
# Ensure the Job model is registered before create_all
from app.models.job import Job, JobStatus, JobType  # noqa: F401
from app.queue.helpers import dequeue, enqueue, mark_failed, mark_succeeded


# ---------------------------------------------------------------------------
# Fixtures – function-scoped so each test gets a clean database
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    """In-memory SQLite engine for isolated tests."""
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture
def db(engine):
    """Provide a fresh database session for each test."""
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()


# ---------------------------------------------------------------------------
# enqueue tests
# ---------------------------------------------------------------------------


class TestEnqueue:
    def test_enqueue_creates_pending_job(self, db):
        job = enqueue(db, JobType.FINANCIAL_ANALYSIS, payload={"key": "val"})
        db.commit()

        assert job.id is not None
        assert job.status == JobStatus.PENDING
        assert job.job_type == JobType.FINANCIAL_ANALYSIS
        assert job.payload == {"key": "val"}
        assert job.attempts == 0
        assert job.max_attempts == 3

    def test_enqueue_custom_max_attempts(self, db):
        job = enqueue(db, JobType.PDF_REPORT, max_attempts=5)
        db.commit()
        assert job.max_attempts == 5

    def test_enqueue_records_created_by(self, db):
        job = enqueue(db, JobType.BULK_INVENTORY_UPDATE, created_by="user-123")
        db.commit()
        assert job.created_by == "user-123"


# ---------------------------------------------------------------------------
# dequeue tests
# ---------------------------------------------------------------------------


class TestDequeue:
    def test_dequeue_returns_oldest_pending(self, db):
        j1 = enqueue(db, JobType.FINANCIAL_ANALYSIS)
        j2 = enqueue(db, JobType.PDF_REPORT)
        db.commit()

        claimed = dequeue(db)
        assert claimed is not None
        assert claimed.id == j1.id
        assert claimed.status == JobStatus.RUNNING
        assert claimed.attempts == 1

    def test_dequeue_returns_none_when_empty(self, db):
        result = dequeue(db)
        assert result is None

    def test_dequeue_skips_running_jobs(self, db):
        enqueue(db, JobType.FINANCIAL_ANALYSIS)
        db.commit()

        first = dequeue(db)
        assert first is not None
        db.commit()

        # Queue should now be empty (the job is RUNNING)
        second = dequeue(db)
        assert second is None

    def test_dequeue_respects_run_after(self, db):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        job = Job(
            job_type=JobType.FINANCIAL_ANALYSIS,
            status=JobStatus.PENDING,
            payload={},
            run_after=future,
        )
        db.add(job)
        db.commit()

        result = dequeue(db)
        assert result is None  # not yet due


# ---------------------------------------------------------------------------
# mark_succeeded tests
# ---------------------------------------------------------------------------


class TestMarkSucceeded:
    def test_mark_succeeded(self, db):
        job = enqueue(db, JobType.FINANCIAL_ANALYSIS)
        db.commit()

        claimed = dequeue(db)
        assert claimed is not None
        mark_succeeded(db, claimed, result={"total_sales": "1000"})
        db.commit()

        refreshed = db.get(Job, claimed.id)
        assert refreshed.status == JobStatus.SUCCEEDED
        assert refreshed.result == {"total_sales": "1000"}
        assert refreshed.finished_at is not None


# ---------------------------------------------------------------------------
# mark_failed / exponential back-off tests
# ---------------------------------------------------------------------------


class TestMarkFailed:
    def test_mark_failed_retries_when_attempts_below_max(self, db):
        job = enqueue(db, JobType.FINANCIAL_ANALYSIS, max_attempts=3)
        db.commit()

        claimed = dequeue(db)  # attempts = 1
        assert claimed is not None
        mark_failed(db, claimed, "transient error", base_delay_seconds=10)
        db.commit()

        refreshed = db.get(Job, claimed.id)
        # Still below max → back to PENDING with run_after in the future
        assert refreshed.status == JobStatus.PENDING
        # Compare naive datetimes (SQLite strips tz info)
        assert refreshed.run_after > datetime.utcnow()
        assert refreshed.error == "transient error"

    def test_mark_failed_permanently_when_max_attempts_reached(self, db):
        job = enqueue(db, JobType.FINANCIAL_ANALYSIS, max_attempts=1)
        db.commit()

        claimed = dequeue(db)  # attempts = 1 == max_attempts
        assert claimed is not None
        mark_failed(db, claimed, "fatal error")
        db.commit()

        refreshed = db.get(Job, claimed.id)
        assert refreshed.status == JobStatus.FAILED
        assert refreshed.finished_at is not None

    def test_backoff_delay_increases_exponentially(self, db):
        """Verify that run_after delay grows with each attempt."""
        job = enqueue(db, JobType.FINANCIAL_ANALYSIS, max_attempts=5)
        db.commit()

        delays = []
        for _ in range(3):
            # Reset to PENDING for each attempt
            job.status = JobStatus.PENDING
            job.run_after = datetime.now(timezone.utc)
            db.flush()

            before = datetime.utcnow()
            claimed = dequeue(db)
            assert claimed is not None
            mark_failed(db, claimed, "err", base_delay_seconds=10)
            db.flush()

            # run_after may be naive (SQLite) or aware; normalise to naive
            ra = job.run_after
            if ra.tzinfo is not None:
                ra = ra.replace(tzinfo=None)
            delta = (ra - before).total_seconds()
            delays.append(delta)

        # Each delay should be larger than the previous
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]

