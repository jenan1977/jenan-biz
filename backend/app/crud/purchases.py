from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.purchase import PurchaseInvoice, PurchaseItem
from ..models.product import Product
from ..models.stock import StockMovement
from ..schemas.purchase import PurchaseInvoiceCreate, PurchaseInvoiceUpdate
from ..config import settings


def _generate_invoice_number(db: Session) -> str:
    year = date.today().year
    count = db.query(PurchaseInvoice).filter(
        PurchaseInvoice.invoice_number.like(f"PO-{year}-%")
    ).count()
    return f"PO-{year}-{count + 1:03d}"


def get_purchase_invoice(db: Session, invoice_id: int) -> Optional[PurchaseInvoice]:
    return db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()


def get_purchase_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[PurchaseInvoice]:
    return db.query(PurchaseInvoice).order_by(PurchaseInvoice.created_at.desc()).offset(skip).limit(limit).all()


def create_purchase_invoice(db: Session, invoice: PurchaseInvoiceCreate, user_id: int) -> PurchaseInvoice:
    items_data = invoice.items
    invoice_data = invoice.model_dump(exclude={"items"})

    subtotal = sum(item.quantity * item.unit_price for item in items_data)
    tax_amount = subtotal * settings.TAX_RATE if invoice.apply_tax else 0.0
    total_amount = subtotal + tax_amount

    db_invoice = PurchaseInvoice(
        **invoice_data,
        invoice_number=_generate_invoice_number(db),
        subtotal=subtotal,
        tax_amount=tax_amount,
        total_amount=total_amount,
        created_by=user_id,
    )
    db.add(db_invoice)
    db.flush()

    for item in items_data:
        total_price = item.quantity * item.unit_price
        db_item = PurchaseItem(
            invoice_id=db_invoice.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=total_price,
        )
        db.add(db_item)

        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
            product.cost_price = item.unit_price

        movement = StockMovement(
            product_id=item.product_id,
            movement_type="PURCHASE",
            quantity=item.quantity,
            reference_id=db_invoice.id,
            reference_type="purchase_invoice",
            notes=f"Purchase invoice {db_invoice.invoice_number}",
            created_by=user_id,
        )
        db.add(movement)

    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def update_purchase_invoice(db: Session, invoice_id: int, invoice: PurchaseInvoiceUpdate) -> Optional[PurchaseInvoice]:
    db_invoice = get_purchase_invoice(db, invoice_id)
    if not db_invoice:
        return None
    for field, value in invoice.model_dump(exclude_unset=True).items():
        setattr(db_invoice, field, value)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def delete_purchase_invoice(db: Session, invoice_id: int) -> bool:
    db_invoice = get_purchase_invoice(db, invoice_id)
    if not db_invoice:
        return False
    db.delete(db_invoice)
    db.commit()
    return True


def update_invoice_file(db: Session, invoice_id: int, file_url: str) -> Optional[PurchaseInvoice]:
    db_invoice = get_purchase_invoice(db, invoice_id)
    if not db_invoice:
        return None
    db_invoice.file_url = file_url
    db.commit()
    db.refresh(db_invoice)
    return db_invoice
