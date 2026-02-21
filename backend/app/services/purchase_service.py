from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.purchase import PurchaseInvoice, PurchaseItem
from app.models.stock import Stock, StockMovement
from app.schemas.purchase_schema import PurchaseInvoiceCreate
from app.services.tax_service import calculate_tax
from app.services.inventory_service import InventoryService


class PurchaseService:

    @staticmethod
    def create_purchase(data: PurchaseInvoiceCreate, db: Session, created_by: int) -> PurchaseInvoice:
        total_amount = sum(item.quantity * item.unit_price for item in data.items)
        if data.apply_tax:
            tax_info = calculate_tax(total_amount)
        else:
            tax_info = {"subtotal": total_amount, "tax_amount": 0.0, "grand_total": total_amount}

        invoice = PurchaseInvoice(
            supplier_id=data.supplier_id,
            invoice_number=data.invoice_number,
            invoice_date=data.invoice_date,
            total_amount=tax_info["subtotal"],
            tax_amount=tax_info["tax_amount"],
            grand_total=tax_info["grand_total"],
            apply_tax=data.apply_tax,
            notes=data.notes,
            status="confirmed",
            created_by=created_by,
        )
        db.add(invoice)
        db.flush()

        for item_data in data.items:
            item = PurchaseItem(
                purchase_invoice_id=invoice.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=round(item_data.quantity * item_data.unit_price, 2),
            )
            db.add(item)
            InventoryService.update_stock_in(db, item_data.product_id, item_data.quantity, "purchase", invoice.id)

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def delete_purchase(invoice_id: int, db: Session):
        invoice = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Purchase invoice not found")
        # Reverse stock for each item and record audit movement
        for item in invoice.items:
            stock = db.query(Stock).filter(Stock.product_id == item.product_id).first()
            if stock:
                stock.current_quantity -= item.quantity
            movement = StockMovement(
                product_id=item.product_id,
                movement_type="OUT",
                quantity=item.quantity,
                reference_type="purchase_reversal",
                reference_id=invoice.id,
                notes=f"Reversal: purchase invoice {invoice.invoice_number} deleted",
            )
            db.add(movement)
        db.delete(invoice)
        db.commit()
