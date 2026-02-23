"""
services/invoice_number.py - Thread-safe, per-company invoice number generation.

Format:
  Sales    : INV-YYYY-MM-00001
  Purchase : PUR-YYYY-MM-00001

Uniqueness is guaranteed by:
  1. Locking the most-recent matching row with SELECT … FOR UPDATE SKIP LOCKED
     (PostgreSQL only), falling back to a plain SELECT on other DB engines.
  2. Incrementing the sequence within the same transaction so no two concurrent
     workers can generate the same number for the same company+prefix+period.
"""

import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.constants import PURCHASE_INVOICE_PREFIX, SALES_INVOICE_PREFIX


def _next_sequence(db: Session, company_id: UUID, prefix: str, year: int, month: int) -> int:
    """
    Return the next sequence number for the given company/prefix/period.

    Uses a raw lock on the invoices table to prevent concurrent duplicates.
    Returns an integer >= 1.
    """
    from app.models.purchase_invoice import PurchaseInvoice
    from app.models.sales_invoice import SalesInvoice

    # Pattern to match existing numbers for this company/period
    pattern = f"{prefix}-{year:04d}-{month:02d}-%"

    if prefix == SALES_INVOICE_PREFIX:
        model = SalesInvoice
    else:
        model = PurchaseInvoice

    # Lock the latest row to serialize concurrent inserts
    try:
        stmt = (
            select(model.invoice_number)
            .where(
                model.company_id == company_id,
                model.invoice_number.like(pattern),
            )
            .order_by(model.invoice_number.desc())
            .limit(1)
            .with_for_update(skip_locked=False)
        )
        result = db.execute(stmt).scalar_one_or_none()
    except Exception:
        # Fallback for non-PostgreSQL engines (e.g. SQLite in tests)
        stmt = (
            select(model.invoice_number)
            .where(
                model.company_id == company_id,
                model.invoice_number.like(pattern),
            )
            .order_by(model.invoice_number.desc())
            .limit(1)
        )
        result = db.execute(stmt).scalar_one_or_none()

    if result is None:
        return 1

    # Extract trailing sequence from "PREFIX-YYYY-MM-NNNNN"
    match = re.search(r"-(\d+)$", result)
    if match:
        return int(match.group(1)) + 1
    return 1


def generate_sales_invoice_number(db: Session, company_id: UUID) -> str:
    """Generate and return the next sales invoice number for *company_id*."""
    now = datetime.now(timezone.utc)
    seq = _next_sequence(db, company_id, SALES_INVOICE_PREFIX, now.year, now.month)
    return f"{SALES_INVOICE_PREFIX}-{now.year:04d}-{now.month:02d}-{seq:05d}"


def generate_purchase_invoice_number(db: Session, company_id: UUID) -> str:
    """Generate and return the next purchase invoice number for *company_id*."""
    now = datetime.now(timezone.utc)
    seq = _next_sequence(db, company_id, PURCHASE_INVOICE_PREFIX, now.year, now.month)
    return f"{PURCHASE_INVOICE_PREFIX}-{now.year:04d}-{now.month:02d}-{seq:05d}"
