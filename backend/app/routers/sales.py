import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from ..database import get_db
from ..models.user import User
from ..schemas.sale import SaleInvoiceCreate, SaleInvoiceUpdate, SaleInvoiceResponse
from ..crud import sales as crud
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/sales", tags=["sales"])


@router.get("/", response_model=List[SaleInvoiceResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud.get_sale_invoices(db, skip=skip, limit=limit)


@router.get("/{invoice_id}", response_model=SaleInvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    invoice = crud.get_sale_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/", response_model=SaleInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice: SaleInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return crud.create_sale_invoice(db, invoice, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{invoice_id}", response_model=SaleInvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice: SaleInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = crud.update_sale_invoice(db, invoice_id, invoice)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not crud.delete_sale_invoice(db, invoice_id):
        raise HTTPException(status_code=404, detail="Invoice not found")


@router.get("/{invoice_id}/pdf")
def generate_pdf(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    invoice = crud.get_sale_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Sale Invoice: {invoice.invoice_number}", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Date: {invoice.date}", styles["Normal"]))
    elements.append(Paragraph(f"Customer: {invoice.customer.name if invoice.customer else 'N/A'}", styles["Normal"]))
    elements.append(Paragraph(f"Status: {invoice.status}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [["Product", "Qty", "Unit Price", "Total"]]
    for item in invoice.items:
        table_data.append([
            item.product.name if item.product else str(item.product_id),
            str(item.quantity),
            f"{item.unit_price:.2f}",
            f"{item.total_price:.2f}",
        ])

    table_data.append(["", "", "Subtotal:", f"{invoice.subtotal:.2f}"])
    if invoice.apply_tax:
        table_data.append(["", "", "Tax:", f"{invoice.tax_amount:.2f}"])
    table_data.append(["", "", "Total:", f"{invoice.total_amount:.2f}"])

    table = Table(table_data, colWidths=[200, 60, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -2), 0.5, colors.black),
        ("FONTNAME", (2, -3), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(table)

    if invoice.notes:
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(f"Notes: {invoice.notes}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=invoice-{invoice.invoice_number}.pdf"},
    )
