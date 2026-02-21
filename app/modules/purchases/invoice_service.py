"""Purchase invoice generation helper."""

from app.modules.purchases.models import Purchase


def generate_purchase_invoice_data(purchase: Purchase) -> dict:
    """Build a structured invoice dict for PDF rendering."""
    return {
        "purchase_number": purchase.purchase_number,
        "date": purchase.created_at.strftime("%Y-%m-%d"),
        "supplier_id": str(purchase.supplier_id) if purchase.supplier_id else None,
        "items": [
            {
                "product_id": str(item.product_id),
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
                "vat_amount": float(item.vat_amount),
                "total": float(item.total),
            }
            for item in purchase.items
        ],
        "subtotal": float(purchase.subtotal),
        "discount_amount": float(purchase.discount_amount),
        "vat_amount": float(purchase.vat_amount),
        "total": float(purchase.total),
    }
