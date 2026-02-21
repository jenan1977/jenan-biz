"""Sales invoice generation helper."""

from app.modules.sales.models import Invoice


def generate_invoice_data(invoice: Invoice) -> dict:
    """Build structured invoice data for PDF/print rendering."""
    return {
        "invoice_number": invoice.invoice_number,
        "date": invoice.created_at.strftime("%Y-%m-%d"),
        "customer_id": str(invoice.customer_id) if invoice.customer_id else None,
        "status": invoice.status.value,
        "items": [
            {
                "product_id": str(item.product_id),
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
                "vat_amount": float(item.vat_amount),
                "total": float(item.total),
            }
            for item in invoice.items
        ],
        "subtotal": float(invoice.subtotal),
        "discount_amount": float(invoice.discount_amount),
        "vat_amount": float(invoice.vat_amount),
        "total": float(invoice.total),
        "amount_paid": float(invoice.amount_paid),
    }
