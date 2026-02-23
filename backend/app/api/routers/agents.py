"""
agents.py - Agents API router.

Endpoints
---------
POST /api/v1/agents/analyze               Enqueue a financial analysis job
POST /api/v1/agents/report                Enqueue a PDF report job
POST /api/v1/agents/inventory/bulk-update Enqueue a bulk inventory update job
GET  /api/v1/agents/jobs/{job_id}         Poll job status / result
GET  /api/v1/agents/jobs/{job_id}/download Download the generated PDF

Authentication
--------------
JWT authentication is required (roles: admin, manager, accountant).
If the JWT dependency module (``app.api.deps``) is not yet available the
router still loads and the endpoints fall back to a permissive no-auth stub
so that the static analytics UI can reach the API during development.
Follow-up PR: replace the stub once ``app.api.deps`` is merged.
"""

from __future__ import annotations

import base64
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.job import Job, JobStatus, JobType
from app.queue.helpers import enqueue

# ---------------------------------------------------------------------------
# JWT / Auth dependency – graceful fallback if not yet available
# ---------------------------------------------------------------------------
# TODO(follow-up): once app.api.deps is merged, replace _get_current_user
#                  with the real dependency from that module.
try:
    from app.api.deps import require_roles  # type: ignore[import]

    _auth_dep = require_roles(["admin", "manager", "accountant"])
except Exception:
    # Stub: no authentication enforced yet – clearly marked for follow-up.
    def _get_current_user_stub() -> Dict[str, Any]:  # type: ignore[return]
        """
        STUB – No JWT validation.  Replace with real auth once deps PR is merged.
        """
        return {"sub": "anonymous", "role": "admin"}

    _auth_dep = Depends(_get_current_user_stub)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    date_from: Optional[str] = Field(None, description="ISO date string e.g. 2025-01-01")
    date_to: Optional[str] = Field(None, description="ISO date string e.g. 2025-12-31")
    company_id: Optional[str] = Field(None, description="UUID of the company")


class ReportRequest(BaseModel):
    date_from: Optional[str] = Field(None, description="ISO date string e.g. 2025-01-01")
    date_to: Optional[str] = Field(None, description="ISO date string e.g. 2025-12-31")
    company_id: Optional[str] = Field(None, description="UUID of the company")


class InventoryUpdateItem(BaseModel):
    inventory_id: str = Field(..., description="UUID of the Inventory row")
    quantity_delta: str = Field(..., description="Decimal string; positive = add, negative = remove")
    reason: Optional[str] = Field(None, description="Audit note")


class BulkInventoryRequest(BaseModel):
    updates: list[InventoryUpdateItem] = Field(..., min_length=1)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def _job_to_dict(job: Job) -> Dict[str, Any]:
    return {
        "job_id": str(job.id),
        "job_type": job.job_type,
        "status": job.status,
        "attempts": job.attempts,
        "max_attempts": job.max_attempts,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "error": job.error,
        "result": job.result,
    }


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
def enqueue_analyze(
    body: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: Any = _auth_dep,
) -> Dict[str, Any]:
    """Enqueue a financial analysis job."""
    job = enqueue(
        db,
        JobType.FINANCIAL_ANALYSIS,
        payload=body.model_dump(exclude_none=True),
        created_by=current_user.get("sub") if isinstance(current_user, dict) else None,
    )
    db.commit()
    return {"job_id": str(job.id), "status": job.status}


@router.post("/report", status_code=status.HTTP_202_ACCEPTED)
def enqueue_report(
    body: ReportRequest,
    db: Session = Depends(get_db),
    current_user: Any = _auth_dep,
) -> Dict[str, Any]:
    """Enqueue a PDF report generation job."""
    job = enqueue(
        db,
        JobType.PDF_REPORT,
        payload=body.model_dump(exclude_none=True),
        created_by=current_user.get("sub") if isinstance(current_user, dict) else None,
    )
    db.commit()
    return {"job_id": str(job.id), "status": job.status}


@router.post("/inventory/bulk-update", status_code=status.HTTP_202_ACCEPTED)
def enqueue_bulk_inventory(
    body: BulkInventoryRequest,
    db: Session = Depends(get_db),
    current_user: Any = _auth_dep,
) -> Dict[str, Any]:
    """Enqueue a bulk inventory update job."""
    payload = {"updates": [item.model_dump(exclude_none=True) for item in body.updates]}
    job = enqueue(
        db,
        JobType.BULK_INVENTORY_UPDATE,
        payload=payload,
        created_by=current_user.get("sub") if isinstance(current_user, dict) else None,
    )
    db.commit()
    return {"job_id": str(job.id), "status": job.status}


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: Any = _auth_dep,
) -> Dict[str, Any]:
    """Poll the status and result of a job."""
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id UUID")

    job = db.get(Job, uid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return _job_to_dict(job)


@router.get("/jobs/{job_id}/download")
def download_job_pdf(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: Any = _auth_dep,
) -> Response:
    """Download the PDF generated by a completed pdf_report job."""
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job_id UUID")

    job = db.get(Job, uid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.job_type != JobType.PDF_REPORT:
        raise HTTPException(status_code=400, detail="Job is not a PDF report job")

    if job.status != JobStatus.SUCCEEDED or not job.result:
        raise HTTPException(
            status_code=409,
            detail=f"PDF not ready – job status is '{job.status}'",
        )

    pdf_b64: Optional[str] = job.result.get("pdf_base64")
    if not pdf_b64:
        raise HTTPException(status_code=500, detail="PDF data missing from job result")

    pdf_bytes = base64.b64decode(pdf_b64)
    filename = job.result.get("filename", "report.pdf")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
