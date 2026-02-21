from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.invoice import Invoice, InvoiceItem
from app.models.product import Product
from app.models.stock import Stock, StockMovement
from app.schemas.invoice_schema import InvoiceCreate
from app.services.tax_service import calculate_tax
from app.services.inventory_service import InventoryService


class InvoiceService:

    @staticmethod
    def create_invoice(data: InvoiceCreate, db: Session, created_by: int) -> Invoice:
        total_amount = 0.0
        total_profit = 0.0
        items_data = []

        for item_data in data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
            item_total = round(item_data.quantity * item_data.unit_price, 2)
            cost_total = round(item_data.quantity * product.purchase_price, 2)
            profit = round(item_total - cost_total, 2)
            total_amount += item_total
            total_profit += profit
            items_data.append({
                "product_id": item_data.product_id,
                "quantity": item_data.quantity,
                "unit_price": item_data.unit_price,
                "cost_price": product.purchase_price,
                "total_price": item_total,
                "profit": profit,
            })

        if data.apply_tax:
            tax_info = calculate_tax(total_amount)
        else:
            tax_info = {"subtotal": total_amount, "tax_amount": 0.0, "grand_total": total_amount}

        invoice = Invoice(
            customer_id=data.customer_id,
            invoice_number=data.invoice_number,
            invoice_date=data.invoice_date,
            total_amount=tax_info["subtotal"],
            tax_amount=tax_info["tax_amount"],
            grand_total=tax_info["grand_total"],
            profit_amount=round(total_profit, 2),
            apply_tax=data.apply_tax,
            notes=data.notes,
            status="confirmed",
            created_by=created_by,
        )
        db.add(invoice)
        db.flush()

        for item_d in items_data:
            item = InvoiceItem(invoice_id=invoice.id, **item_d)
            db.add(item)
            InventoryService.update_stock_out(db, item_d["product_id"], item_d["quantity"], "invoice", invoice.id)

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def delete_invoice(invoice_id: int, db: Session):
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")
        # Reverse stock for each item and record audit movement
        for item in invoice.items:
            stock = db.query(Stock).filter(Stock.product_id == item.product_id).first()
            if stock:
                stock.current_quantity += item.quantity
            movement = StockMovement(
                product_id=item.product_id,
                movement_type="IN",
                quantity=item.quantity,
                reference_type="invoice_reversal",
                reference_id=invoice.id,
                notes=f"Reversal: sales invoice {invoice.invoice_number} deleted",
            )
            db.add(movement)
        db.delete(invoice)
        db.commit()
