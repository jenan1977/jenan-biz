"""PDF invoice generation using ReportLab (stub)."""


def generate_pdf_invoice(invoice_data: dict) -> bytes:
    """
    Generate a PDF for the given invoice data.
    Returns PDF bytes.

    Note: Requires 'reportlab' package. Install with: pip install reportlab
    """
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"Invoice: {invoice_data['invoice_number']}", styles['Title']))
        elements.append(Paragraph(f"Date: {invoice_data['date']}", styles['Normal']))

        data = [["Product", "Qty", "Unit Price", "VAT", "Total"]]
        for item in invoice_data["items"]:
            data.append([
                item["product_id"],
                str(item["quantity"]),
                f"{item['unit_price']:.2f}",
                f"{item['vat_amount']:.2f}",
                f"{item['total']:.2f}",
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Paragraph(f"Total: {invoice_data['total']:.2f}", styles['Normal']))

        doc.build(elements)
        return buffer.getvalue()
    except ImportError:
        return b"PDF generation requires reportlab package."
