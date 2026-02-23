"""
financial_analysis.py - Handler for FINANCIAL_ANALYSIS jobs.

Payload schema:
    {
        "company_id": "<uuid>",
        "from_date": "YYYY-MM-DD",
        "to_date":   "YYYY-MM-DD"
    }

Result schema:
    {
        "total_sales":    <float>,
        "total_purchases": <float>,
        "top_customers":  [{"customer_id": "...", "name": "...", "total": <float>}, ...],
        "low_stock_alerts": [{"product_id": "...", "name": "...", "available": <float>}, ...]
    }
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.job import Job
from app.models.product import Product
from app.models.purchase_invoice import PurchaseInvoice
from app.models.sales_invoice import SalesInvoice


def handle_financial_analysis(db: Session, job: Job) -> Dict[str, Any]:
    """Execute a FINANCIAL_ANALYSIS job and return the result dict."""
    payload = job.payload
    company_id = uuid.UUID(payload["company_id"])
    from_date = datetime.fromisoformat(payload["from_date"]).replace(tzinfo=timezone.utc)
    to_date = datetime.fromisoformat(payload["to_date"]).replace(
        hour=23, minute=59, second=59, tzinfo=timezone.utc
    )

    # --- Total sales ---
    sales_row = db.execute(
        select(func.coalesce(func.sum(SalesInvoice.total_amount), 0))
        .where(SalesInvoice.company_id == company_id)
        .where(SalesInvoice.invoice_date >= from_date)
        .where(SalesInvoice.invoice_date <= to_date)
        .where(SalesInvoice.is_deleted.is_(False))
    ).scalar()
    total_sales = float(sales_row or 0)

    # --- Total purchases ---
    purchases_row = db.execute(
        select(func.coalesce(func.sum(PurchaseInvoice.total_amount), 0))
        .where(PurchaseInvoice.company_id == company_id)
        .where(PurchaseInvoice.invoice_date >= from_date)
        .where(PurchaseInvoice.invoice_date <= to_date)
        .where(PurchaseInvoice.is_deleted.is_(False))
    ).scalar()
    total_purchases = float(purchases_row or 0)

    # --- Top customers (by total invoice amount) ---
    top_customers_rows = db.execute(
        select(
            Customer.id,
            Customer.name,
            func.coalesce(func.sum(SalesInvoice.total_amount), 0).label("total"),
        )
        .join(SalesInvoice, SalesInvoice.customer_id == Customer.id)
        .where(SalesInvoice.company_id == company_id)
        .where(SalesInvoice.invoice_date >= from_date)
        .where(SalesInvoice.invoice_date <= to_date)
        .where(SalesInvoice.is_deleted.is_(False))
        .group_by(Customer.id, Customer.name)
        .order_by(func.sum(SalesInvoice.total_amount).desc())
        .limit(10)
    ).all()
    top_customers = [
        {"customer_id": str(r.id), "name": r.name, "total": float(r.total)}
        for r in top_customers_rows
    ]

    # --- Low-stock alerts ---
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
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "top_customers": top_customers,
        "low_stock_alerts": low_stock_alerts,
    }
