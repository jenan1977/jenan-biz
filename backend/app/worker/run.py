"""
run.py - Background worker that polls the PostgreSQL job queue.

Usage
-----
    PYTHONPATH=backend python -m app.worker.run

The worker runs in an infinite loop, sleeping ``WORKER_POLL_INTERVAL`` seconds
between polls when the queue is empty.
"""

from __future__ import annotations

import logging
import os
import signal
import time
import traceback
from types import FrameType
from typing import Optional

from app.core.database import SessionLocal
from app.models.job import JobType
from app.queue.helpers import dequeue, mark_failed, mark_succeeded
from app.worker.handlers import bulk_inventory, financial_analysis, pdf_report

logger = logging.getLogger(__name__)

# Seconds to sleep when the queue is empty
POLL_INTERVAL: int = int(os.getenv("WORKER_POLL_INTERVAL", "5"))

# Map job type → handler module
_HANDLERS = {
    JobType.FINANCIAL_ANALYSIS: financial_analysis.run,
    JobType.PDF_REPORT: pdf_report.run,
    JobType.BULK_INVENTORY_UPDATE: bulk_inventory.run,
}

_running = True


def _shutdown(signum: int, frame: Optional[FrameType]) -> None:  # noqa: ARG001
    global _running
    logger.info("Shutdown signal received – finishing current job then stopping.")
    _running = False


signal.signal(signal.SIGTERM, _shutdown)
signal.signal(signal.SIGINT, _shutdown)


def process_one() -> bool:
    """
    Claim and process one job from the queue.

    Returns
    -------
    bool
        ``True`` if a job was processed, ``False`` if the queue was empty.
    """
    db = SessionLocal()
    try:
        job = dequeue(db)
        if job is None:
            db.commit()
            return False

        logger.info("Processing job %s (type=%s, attempt=%d)", job.id, job.job_type, job.attempts)

        handler = _HANDLERS.get(job.job_type)
        if handler is None:
            mark_failed(db, job, f"No handler registered for job type: {job.job_type}")
            db.commit()
            return True

        try:
            result = handler(db, job.payload or {})
            mark_succeeded(db, job, result)
            db.commit()
            logger.info("Job %s succeeded.", job.id)
        except Exception:
            error_msg = traceback.format_exc()
            logger.error("Job %s failed:\n%s", job.id, error_msg)
            mark_failed(db, job, error_msg)
            db.commit()

        return True
    except Exception:
        logger.exception("Unexpected error in worker loop")
        db.rollback()
        return False
    finally:
        db.close()


def run() -> None:
    """Main worker loop."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("Worker started. Poll interval: %d s", POLL_INTERVAL)

    while _running:
        processed = process_one()
        if not processed:
            time.sleep(POLL_INTERVAL)

    logger.info("Worker stopped.")


if __name__ == "__main__":
    run()
