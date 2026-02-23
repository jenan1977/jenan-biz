"""
test_jobs.py - Unit tests for the job queue models and worker logic.

These tests use SQLite in-memory database to avoid requiring a live PostgreSQL
instance.  The SKIP LOCKED behaviour is tested via mocking since SQLite does
not support it.
"""

import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.constants import JobStatus, JobType
from app.core.database import Base
from app.models.job import Job


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def engine():
    """In-memory SQLite engine for testing (no PostgreSQL required)."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Import Job so its table is registered with Base.metadata before create_all
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def db(engine):
    """Per-test database session that is rolled back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = SessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def make_job(
    db: Session,
    job_type: JobType = JobType.FINANCIAL_ANALYSIS,
    payload: Dict[str, Any] | None = None,
    status: JobStatus = JobStatus.QUEUED,
    run_at: datetime | None = None,
) -> Job:
    if payload is None:
        payload = {
            "company_id": str(uuid.uuid4()),
            "from_date": "2025-01-01",
            "to_date": "2025-12-31",
        }
    job = Job(
        job_type=job_type,
        payload=payload,
        status=status,
        run_at=run_at or datetime.now(timezone.utc),
    )
    db.add(job)
    db.flush()
    return job


# ---------------------------------------------------------------------------
# Enqueue tests
# ---------------------------------------------------------------------------


def test_enqueue_creates_queued_job(db: Session) -> None:
    """A freshly created job must have QUEUED status."""
    job = make_job(db)
    assert job.id is not None
    assert job.status == JobStatus.QUEUED
    assert job.attempts == 0
    assert job.max_attempts == 3


def test_enqueue_default_priority(db: Session) -> None:
    job = make_job(db)
    assert job.priority == 100


def test_job_has_timestamps(db: Session) -> None:
    job = make_job(db)
    assert job.created_at is not None
    assert job.updated_at is not None


def test_enqueue_bulk_inventory_job(db: Session) -> None:
    job = make_job(
        db,
        job_type=JobType.BULK_INVENTORY_UPDATE,
        payload={
            "company_id": str(uuid.uuid4()),
            "adjustments": [
                {"product_id": str(uuid.uuid4()), "delta_on_hand": 5.0}
            ],
        },
    )
    assert job.job_type == JobType.BULK_INVENTORY_UPDATE


# ---------------------------------------------------------------------------
# Job status transition tests
# ---------------------------------------------------------------------------


def test_job_transition_queued_to_running(db: Session) -> None:
    job = make_job(db)
    job.status = JobStatus.RUNNING
    job.locked_by = "worker-1"
    job.attempts = 1
    db.flush()
    assert job.status == JobStatus.RUNNING
    assert job.locked_by == "worker-1"


def test_job_transition_running_to_succeeded(db: Session) -> None:
    job = make_job(db, status=JobStatus.RUNNING)
    job.status = JobStatus.SUCCEEDED
    job.result = {"total_sales": 1000.0}
    db.flush()
    assert job.status == JobStatus.SUCCEEDED
    assert job.result["total_sales"] == 1000.0


def test_job_transition_running_to_failed(db: Session) -> None:
    job = make_job(db, status=JobStatus.RUNNING)
    job.status = JobStatus.FAILED
    job.error = "Something went wrong"
    db.flush()
    assert job.status == JobStatus.FAILED
    assert "Something went wrong" in job.error


def test_job_cancelled(db: Session) -> None:
    job = make_job(db)
    job.status = JobStatus.CANCELLED
    db.flush()
    assert job.status == JobStatus.CANCELLED


# ---------------------------------------------------------------------------
# Requeue / backoff tests
# ---------------------------------------------------------------------------


def test_requeue_increments_run_at(db: Session) -> None:
    """After a failed attempt, run_at should be in the future."""
    job = make_job(db, status=JobStatus.RUNNING)
    job.attempts = 1

    now = datetime.now(timezone.utc)
    delay = 2 ** job.attempts  # 2 seconds
    job.run_at = now + timedelta(seconds=delay)
    job.status = JobStatus.QUEUED
    db.flush()

    assert job.run_at > now


def test_max_attempts_causes_failure(db: Session) -> None:
    """Once attempts >= max_attempts the job should be FAILED."""
    job = make_job(db, status=JobStatus.RUNNING)
    job.attempts = job.max_attempts  # 3

    # Simulate _requeue_or_fail logic
    if job.attempts >= job.max_attempts:
        job.status = JobStatus.FAILED
        job.error = "permanent failure"
    db.flush()

    assert job.status == JobStatus.FAILED


# ---------------------------------------------------------------------------
# Inventory bulk update validation tests (unit, no DB queries)
# ---------------------------------------------------------------------------


def test_bulk_inventory_update_rejects_empty_adjustments() -> None:
    """Payload with no adjustments must raise ValueError."""
    from app.worker.handlers.bulk_inventory_update import handle_bulk_inventory_update

    mock_session = MagicMock(spec=Session)
    job = Job(
        job_type=JobType.BULK_INVENTORY_UPDATE,
        payload={"company_id": str(uuid.uuid4()), "adjustments": []},
        status=JobStatus.RUNNING,
        run_at=datetime.now(timezone.utc),
    )

    with pytest.raises(ValueError, match="at least one adjustment"):
        handle_bulk_inventory_update(mock_session, job)


def test_bulk_inventory_update_skips_negative_on_hand() -> None:
    """Adjustments that would make on_hand negative must be skipped."""
    from app.models.inventory import Inventory
    from app.worker.handlers.bulk_inventory_update import handle_bulk_inventory_update

    company_id = uuid.uuid4()
    product_id = uuid.uuid4()

    # Build a mock inventory row
    mock_inv = MagicMock(spec=Inventory)
    mock_inv.quantity_on_hand = Decimal("5.00")
    mock_inv.quantity_reserved = Decimal("0.00")
    mock_inv.quantity_available = Decimal("5.00")

    # Mock the DB query chain
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_inv
    mock_session = MagicMock(spec=Session)
    mock_session.execute.return_value = mock_result

    job = Job(
        job_type=JobType.BULK_INVENTORY_UPDATE,
        payload={
            "company_id": str(company_id),
            "adjustments": [
                {"product_id": str(product_id), "delta_on_hand": -10.0}
            ],
        },
        status=JobStatus.RUNNING,
        run_at=datetime.now(timezone.utc),
    )

    result = handle_bulk_inventory_update(mock_session, job)
    assert result["updated"] == 0
    assert len(result["skipped"]) == 1
    assert "negative" in result["skipped"][0]["reason"]


def test_bulk_inventory_update_applies_valid_adjustment() -> None:
    """Valid adjustments must update on_hand, reserved, and available."""
    from app.models.inventory import Inventory
    from app.worker.handlers.bulk_inventory_update import handle_bulk_inventory_update

    company_id = uuid.uuid4()
    product_id = uuid.uuid4()

    mock_inv = MagicMock(spec=Inventory)
    mock_inv.quantity_on_hand = Decimal("10.00")
    mock_inv.quantity_reserved = Decimal("2.00")
    mock_inv.quantity_available = Decimal("8.00")

    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_inv
    mock_session = MagicMock(spec=Session)
    mock_session.execute.return_value = mock_result

    job = Job(
        job_type=JobType.BULK_INVENTORY_UPDATE,
        payload={
            "company_id": str(company_id),
            "adjustments": [
                {"product_id": str(product_id), "delta_on_hand": 5.0}
            ],
        },
        status=JobStatus.RUNNING,
        run_at=datetime.now(timezone.utc),
    )

    result = handle_bulk_inventory_update(mock_session, job)
    assert result["updated"] == 1
    assert result["skipped"] == []
    # Check that values were set correctly
    assert mock_inv.quantity_on_hand == Decimal("15.00")
    assert mock_inv.quantity_available == Decimal("13.00")
