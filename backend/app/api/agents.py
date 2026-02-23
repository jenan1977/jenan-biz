"""
agents.py - Agents API router: enqueue jobs and poll results.

Endpoints
---------
POST /api/v1/agents/analyze               -> enqueue FINANCIAL_ANALYSIS
POST /api/v1/agents/report                -> enqueue PDF_REPORT
POST /api/v1/agents/inventory/bulk-update -> enqueue BULK_INVENTORY_UPDATE
GET  /api/v1/agents/jobs/{job_id}         -> get job status + result
GET  /api/v1/agents/jobs/{job_id}/download-> download PDF (PDF_REPORT only)
GET  /api/v1/companies/{company_id}/analytics/summary -> direct stats
"""

from __future__ import annotations

import base64
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import TokenData, require_agent_role
from app.core.constants import JobStatus, JobType, UserRole
from app.core.database import get_db
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.job import Job
from app.models.product import Product
from app.models.purchase_invoice import PurchaseInvoice
from app.models.sales_invoice import SalesInvoice

router = APIRouter(prefix="/api/v1", tags=["agents"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    company_id: uuid.UUID
    from_date: str  # YYYY-MM-DD
    to_date: str  # YYYY-MM-DD


class ReportRequest(BaseModel):
    company_id: uuid.UUID
    from_date: str
    to_date: str


class InventoryAdjustment(BaseModel):
    product_id: uuid.UUID
    delta_on_hand: float = 0.0
    delta_reserved: float = 0.0


class BulkInventoryRequest(BaseModel):
    company_id: uuid.UUID
    adjustments: List[InventoryAdjustment]

    @field_validator("adjustments")
    @classmethod
    def at_least_one(cls, v: list) -> list:
        if not v:
            raise ValueError("adjustments must not be empty")
        return v


class JobResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    job_type: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _assert_company_access(user: TokenData, company_id: uuid.UUID) -> None:
    """Raise 403 if the user cannot access the requested company."""
    if user.role != UserRole.ADMIN and user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to the requested company is not allowed",
        )


def _enqueue(
    db: Session,
    job_type: JobType,
    company_id: Optional[uuid.UUID],
    payload: Dict[str, Any],
) -> Job:
    job = Job(
        job_type=job_type,
        company_id=company_id,
        payload=payload,
        status=JobStatus.QUEUED,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _get_job_or_404(db: Session, job_id: uuid.UUID) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/agents/analyze", response_model=JobResponse, status_code=202)
def enqueue_financial_analysis(
    body: AnalyzeRequest,
    db: Session = Depends(get_db),
    user: TokenData = Depends(require_agent_role),
) -> JobResponse:
    """Enqueue a FINANCIAL_ANALYSIS job and return the job_id."""
    _assert_company_access(user, body.company_id)
    job = _enqueue(
        db,
        JobType.FINANCIAL_ANALYSIS,
        body.company_id,
        {
            "company_id": str(body.company_id),
            "from_date": body.from_date,
            "to_date": body.to_date,
        },
    )
    return JobResponse(
        job_id=job.id,
        status=job.status,
        job_type=job.job_type,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post("/agents/report", response_model=JobResponse, status_code=202)
def enqueue_pdf_report(
    body: ReportRequest,
    db: Session = Depends(get_db),
    user: TokenData = Depends(require_agent_role),
) -> JobResponse:
    """Enqueue a PDF_REPORT job and return the job_id."""
    _assert_company_access(user, body.company_id)
    job = _enqueue(
        db,
        JobType.PDF_REPORT,
        body.company_id,
        {
            "company_id": str(body.company_id),
            "from_date": body.from_date,
            "to_date": body.to_date,
        },
    )
    return JobResponse(
        job_id=job.id,
        status=job.status,
        job_type=job.job_type,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.post("/agents/inventory/bulk-update", response_model=JobResponse, status_code=202)
def enqueue_bulk_inventory_update(
    body: BulkInventoryRequest,
    db: Session = Depends(get_db),
    user: TokenData = Depends(require_agent_role),
) -> JobResponse:
    """Enqueue a BULK_INVENTORY_UPDATE job and return the job_id."""
    _assert_company_access(user, body.company_id)
    job = _enqueue(
        db,
        JobType.BULK_INVENTORY_UPDATE,
        body.company_id,
        {
            "company_id": str(body.company_id),
            "adjustments": [
                {
                    "product_id": str(a.product_id),
                    "delta_on_hand": a.delta_on_hand,
                    "delta_reserved": a.delta_reserved,
                }
                for a in body.adjustments
            ],
        },
    )
    return JobResponse(
        job_id=job.id,
        status=job.status,
        job_type=job.job_type,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/agents/jobs/{job_id}", response_model=JobResponse)
def get_job_status(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: TokenData = Depends(require_agent_role),
) -> JobResponse:
    """Return current status and result of a job."""
    job = _get_job_or_404(db, job_id)
    if job.company_id is not None:
        _assert_company_access(user, job.company_id)
    return JobResponse(
        job_id=job.id,
        status=job.status,
        job_type=job.job_type,
        result=job.result,
        error=job.error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/agents/jobs/{job_id}/download")
def download_pdf_report(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: TokenData = Depends(require_agent_role),
) -> Response:
    """Download the generated PDF for a completed PDF_REPORT job."""
    job = _get_job_or_404(db, job_id)
    if job.company_id is not None:
        _assert_company_access(user, job.company_id)
    if job.job_type != JobType.PDF_REPORT:
        raise HTTPException(status_code=400, detail="Job is not a PDF_REPORT")
    if job.status != JobStatus.SUCCEEDED:
        raise HTTPException(
            status_code=409, detail=f"Job is not SUCCEEDED (status={job.status})"
        )
    if not job.result or "pdf_base64" not in job.result:
        raise HTTPException(status_code=500, detail="PDF data missing from job result")

    pdf_bytes = base64.b64decode(job.result["pdf_base64"])
    filename = job.result.get("filename", f"report_{job_id}.pdf")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/companies/{company_id}/analytics/summary")
def get_analytics_summary(
    company_id: uuid.UUID,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    user: TokenData = Depends(require_agent_role),
) -> Dict[str, Any]:
    """Direct (synchronous) analytics summary for a company."""
    _assert_company_access(user, company_id)

    now = datetime.now(timezone.utc)
    from_dt = (
        datetime.fromisoformat(from_date).replace(tzinfo=timezone.utc)
        if from_date
        else datetime(now.year, 1, 1, tzinfo=timezone.utc)
    )
    to_dt = (
        datetime.fromisoformat(to_date).replace(
            hour=23, minute=59, second=59, tzinfo=timezone.utc
        )
        if to_date
        else now
    )

    total_sales = float(
        db.execute(
            select(func.coalesce(func.sum(SalesInvoice.total_amount), 0))
            .where(SalesInvoice.company_id == company_id)
            .where(SalesInvoice.invoice_date >= from_dt)
            .where(SalesInvoice.invoice_date <= to_dt)
            .where(SalesInvoice.is_deleted.is_(False))
        ).scalar()
        or 0
    )

    total_purchases = float(
        db.execute(
            select(func.coalesce(func.sum(PurchaseInvoice.total_amount), 0))
            .where(PurchaseInvoice.company_id == company_id)
            .where(PurchaseInvoice.invoice_date >= from_dt)
            .where(PurchaseInvoice.invoice_date <= to_dt)
            .where(PurchaseInvoice.is_deleted.is_(False))
        ).scalar()
        or 0
    )

    top_customers_rows = db.execute(
        select(
            Customer.id,
            Customer.name,
            func.coalesce(func.sum(SalesInvoice.total_amount), 0).label("total"),
        )
        .join(SalesInvoice, SalesInvoice.customer_id == Customer.id)
        .where(SalesInvoice.company_id == company_id)
        .where(SalesInvoice.invoice_date >= from_dt)
        .where(SalesInvoice.invoice_date <= to_dt)
        .where(SalesInvoice.is_deleted.is_(False))
        .group_by(Customer.id, Customer.name)
        .order_by(func.sum(SalesInvoice.total_amount).desc())
        .limit(10)
    ).all()
    top_customers = [
        {"customer_id": str(r.id), "name": r.name, "total": float(r.total)}
        for r in top_customers_rows
    ]

    low_stock_rows = db.execute(
        select(Product.id, Product.name, Inventory.quantity_available)
        .join(Inventory, Inventory.product_id == Product.id)
        .where(Inventory.company_id == company_id)
        .where(
            Inventory.quantity_available
            <= func.coalesce(Inventory.reorder_level, 0)
        )
    ).all()
    low_stock_alerts = [
        {
            "product_id": str(r.id),
            "name": r.name,
            "available": float(r.quantity_available),
        }
        for r in low_stock_rows
    ]

    return {
        "company_id": str(company_id),
        "from_date": from_dt.date().isoformat(),
        "to_date": to_dt.date().isoformat(),
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "top_customers": top_customers,
        "low_stock_alerts": low_stock_alerts,
    }
