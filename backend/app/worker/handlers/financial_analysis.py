"""
financial_analysis.py - Handler: aggregate sales/purchases and flag low stock.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.sales_invoice import SalesInvoice
from app.models.purchase_invoice import PurchaseInvoice


def run(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform financial analysis.

    Payload keys (all optional)
    ---------------------------
    date_from : str  ISO-8601 date string, e.g. "2025-01-01"
    date_to   : str  ISO-8601 date string, e.g. "2025-12-31"
    company_id: str  UUID of the company to analyse (analyses all if absent)

    Returns a dict with:
    - total_sales        : Decimal
    - total_purchases    : Decimal
    - low_stock_alerts   : list[dict]
    - top_customers      : list[dict]  (top 10 by total spend)
    """
    from datetime import datetime, timezone

    date_from_str: str | None = payload.get("date_from")
    date_to_str: str | None = payload.get("date_to")
    company_id_str: str | None = payload.get("company_id")

    date_from = datetime.fromisoformat(date_from_str).replace(tzinfo=timezone.utc) if date_from_str else None
    date_to = datetime.fromisoformat(date_to_str).replace(tzinfo=timezone.utc) if date_to_str else None

    # ── Sales totals ──────────────────────────────────────────────────
    sales_q = db.query(func.coalesce(func.sum(SalesInvoice.total_amount), Decimal("0")))
    if company_id_str:
        import uuid
        sales_q = sales_q.filter(SalesInvoice.company_id == uuid.UUID(company_id_str))
    if date_from:
        sales_q = sales_q.filter(SalesInvoice.invoice_date >= date_from)
    if date_to:
        sales_q = sales_q.filter(SalesInvoice.invoice_date <= date_to)
    total_sales: Decimal = sales_q.scalar() or Decimal("0")

    # ── Purchase totals ───────────────────────────────────────────────
    purch_q = db.query(func.coalesce(func.sum(PurchaseInvoice.total_amount), Decimal("0")))
    if company_id_str:
        import uuid
        purch_q = purch_q.filter(PurchaseInvoice.company_id == uuid.UUID(company_id_str))
    if date_from:
        purch_q = purch_q.filter(PurchaseInvoice.invoice_date >= date_from)
    if date_to:
        purch_q = purch_q.filter(PurchaseInvoice.invoice_date <= date_to)
    total_purchases: Decimal = purch_q.scalar() or Decimal("0")

    # ── Low stock alerts ──────────────────────────────────────────────
    inv_q = db.query(Inventory).filter(
        Inventory.reorder_level.isnot(None),
        Inventory.quantity_available <= Inventory.reorder_level,
    )
    if company_id_str:
        import uuid
        inv_q = inv_q.filter(Inventory.company_id == uuid.UUID(company_id_str))

    low_stock_alerts: List[Dict[str, Any]] = []
    for inv in inv_q.all():
        low_stock_alerts.append(
            {
                "inventory_id": str(inv.id),
                "product_id": str(inv.product_id),
                "quantity_available": str(inv.quantity_available),
                "reorder_level": str(inv.reorder_level),
            }
        )

    # ── Top customers ─────────────────────────────────────────────────
    top_q = (
        db.query(
            SalesInvoice.customer_id,
            func.sum(SalesInvoice.total_amount).label("total_spend"),
        )
        .group_by(SalesInvoice.customer_id)
        .order_by(func.sum(SalesInvoice.total_amount).desc())
        .limit(10)
    )
    if company_id_str:
        import uuid
        top_q = top_q.filter(SalesInvoice.company_id == uuid.UUID(company_id_str))
    if date_from:
        top_q = top_q.filter(SalesInvoice.invoice_date >= date_from)
    if date_to:
        top_q = top_q.filter(SalesInvoice.invoice_date <= date_to)

    top_customers: List[Dict[str, Any]] = []
    for customer_id, total_spend in top_q.all():
        customer = db.get(Customer, customer_id)
        top_customers.append(
            {
                "customer_id": str(customer_id),
                "customer_name": customer.name if customer else None,
                "total_spend": str(total_spend),
            }
        )

    return {
        "total_sales": str(total_sales),
        "total_purchases": str(total_purchases),
        "low_stock_alerts": low_stock_alerts,
        "top_customers": top_customers,
    }
