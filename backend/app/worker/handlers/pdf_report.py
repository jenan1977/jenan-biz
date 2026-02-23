"""
pdf_report.py - Handler for PDF_REPORT jobs.

Payload schema:
    {
        "company_id": "<uuid>",
        "from_date":  "YYYY-MM-DD",
        "to_date":    "YYYY-MM-DD"
    }

Result schema:
    {
        "pdf_base64": "<base64-encoded PDF bytes>",
        "filename":   "report_<company_id>_<from>_<to>.pdf"
    }
"""

import base64
import io
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


def _build_pdf(
    company_id: uuid.UUID,
    from_date: datetime,
    to_date: datetime,
    total_sales: float,
    total_purchases: float,
    top_customers: list,
    low_stock: list,
) -> bytes:
    """Render a minimal PDF summary using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 2 * cm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2 * cm, y, "Business Analytics Report")
    y -= 1 * cm

    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Company: {company_id}")
    y -= 0.6 * cm
    c.drawString(
        2 * cm,
        y,
        f"Period: {from_date.date()} to {to_date.date()}",
    )
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Financial Summary")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)
    c.drawString(2 * cm, y, f"Total Sales:     {total_sales:,.2f}")
    y -= 0.6 * cm
    c.drawString(2 * cm, y, f"Total Purchases: {total_purchases:,.2f}")
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Top Customers")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)
    for cust in top_customers[:10]:
        c.drawString(2 * cm, y, f"  {cust['name']}: {cust['total']:,.2f}")
        y -= 0.6 * cm
        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm

    y -= 0.4 * cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y, "Low-Stock Alerts")
    y -= 0.7 * cm
    c.setFont("Helvetica", 10)
    if low_stock:
        for item in low_stock[:20]:
            c.drawString(
                2 * cm,
                y,
                f"  {item['name']}: {item['available']} available",
            )
            y -= 0.6 * cm
            if y < 3 * cm:
                c.showPage()
                y = height - 2 * cm
    else:
        c.drawString(2 * cm, y, "  No low-stock items.")

    c.save()
    return buf.getvalue()


def handle_pdf_report(db: Session, job: Job) -> Dict[str, Any]:
    """Execute a PDF_REPORT job and return base64-encoded PDF."""
    payload = job.payload
    company_id = uuid.UUID(payload["company_id"])
    from_date = datetime.fromisoformat(payload["from_date"]).replace(tzinfo=timezone.utc)
    to_date = datetime.fromisoformat(payload["to_date"]).replace(
        hour=23, minute=59, second=59, tzinfo=timezone.utc
    )

    # Reuse financial analysis logic inline
    total_sales = float(
        db.execute(
            select(func.coalesce(func.sum(SalesInvoice.total_amount), 0))
            .where(SalesInvoice.company_id == company_id)
            .where(SalesInvoice.invoice_date >= from_date)
            .where(SalesInvoice.invoice_date <= to_date)
            .where(SalesInvoice.is_deleted.is_(False))
        ).scalar()
        or 0
    )

    total_purchases = float(
        db.execute(
            select(func.coalesce(func.sum(PurchaseInvoice.total_amount), 0))
            .where(PurchaseInvoice.company_id == company_id)
            .where(PurchaseInvoice.invoice_date >= from_date)
            .where(PurchaseInvoice.invoice_date <= to_date)
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

    low_stock_rows = db.execute(
        select(Product.id, Product.name, Inventory.quantity_available)
        .join(Inventory, Inventory.product_id == Product.id)
        .where(Inventory.company_id == company_id)
        .where(
            Inventory.quantity_available
            <= func.coalesce(Inventory.reorder_level, 0)
        )
    ).all()
    low_stock = [
        {"product_id": str(r.id), "name": r.name, "available": float(r.quantity_available)}
        for r in low_stock_rows
    ]

    pdf_bytes = _build_pdf(
        company_id, from_date, to_date, total_sales, total_purchases, top_customers, low_stock
    )
    filename = (
        f"report_{company_id}_{from_date.date()}_{to_date.date()}.pdf"
    )

    return {
        "pdf_base64": base64.b64encode(pdf_bytes).decode("ascii"),
        "filename": filename,
    }
