"""
pdf_report.py - Handler: generate a PDF financial report using reportlab.

The generated PDF is Base64-encoded and stored in ``job.result`` as::

    {
        "pdf_base64": "<base64-string>",
        "filename": "financial_report_<date>.pdf",
        "content_type": "application/pdf"
    }
"""

from __future__ import annotations

import base64
import io
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy.orm import Session

from app.worker.handlers import financial_analysis


def run(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a PDF financial report.

    Accepts the same payload keys as the ``financial_analysis`` handler
    (``date_from``, ``date_to``, ``company_id``).
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        from reportlab.lib import colors
    except ImportError as exc:
        raise RuntimeError(
            "reportlab is required for PDF generation. "
            "Install it with: pip install reportlab==4.2.5"
        ) from exc

    # ── Fetch analysis data ───────────────────────────────────────────
    analysis = financial_analysis.run(db, payload)

    # ── Build PDF in memory ───────────────────────────────────────────
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    date_label = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    elements.append(Paragraph("Jenan-Biz Financial Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated: {date_label}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Summary table
    summary_data = [
        ["Metric", "Value"],
        ["Total Sales", analysis["total_sales"]],
        ["Total Purchases", analysis["total_purchases"]],
        ["Low Stock Items", str(len(analysis["low_stock_alerts"]))],
    ]
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ECF0F1")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Top customers table
    if analysis["top_customers"]:
        elements.append(Paragraph("Top Customers", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        cust_data = [["Customer", "Total Spend"]]
        for c in analysis["top_customers"]:
            cust_data.append([c.get("customer_name") or c["customer_id"], c["total_spend"]])
        cust_table = Table(cust_data, colWidths=[250, 150])
        cust_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ECF0F1")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(cust_table)

    # Low stock alerts table
    if analysis["low_stock_alerts"]:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("Low Stock Alerts", styles["Heading2"]))
        elements.append(Spacer(1, 8))
        stock_data = [["Product ID", "Available", "Reorder Level"]]
        for item in analysis["low_stock_alerts"]:
            stock_data.append(
                [item["product_id"], item["quantity_available"], item["reorder_level"]]
            )
        stock_table = Table(stock_data, colWidths=[200, 100, 100])
        stock_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E74C3C")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FADBD8")]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("PADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        elements.append(stock_table)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()

    filename = f"financial_report_{date_label}.pdf"
    return {
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
        "filename": filename,
        "content_type": "application/pdf",
        "analysis": analysis,
    }
