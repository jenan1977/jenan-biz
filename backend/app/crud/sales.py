from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.sale import SaleInvoice, SaleItem
from ..models.product import Product
from ..models.stock import StockMovement
from ..schemas.sale import SaleInvoiceCreate, SaleInvoiceUpdate
from ..config import settings


def _generate_invoice_number(db: Session) -> str:
    year = date.today().year
    count = db.query(SaleInvoice).filter(
        SaleInvoice.invoice_number.like(f"INV-{year}-%")
    ).count()
    return f"INV-{year}-{count + 1:03d}"


def get_sale_invoice(db: Session, invoice_id: int) -> Optional[SaleInvoice]:
    return db.query(SaleInvoice).filter(SaleInvoice.id == invoice_id).first()


def get_sale_invoices(db: Session, skip: int = 0, limit: int = 100) -> List[SaleInvoice]:
    return db.query(SaleInvoice).order_by(SaleInvoice.created_at.desc()).offset(skip).limit(limit).all()


def create_sale_invoice(db: Session, invoice: SaleInvoiceCreate, user_id: int) -> SaleInvoice:
    items_data = invoice.items
    invoice_data = invoice.model_dump(exclude={"items"})

    subtotal = 0.0
    profit = 0.0

    db_invoice = SaleInvoice(
        **invoice_data,
        invoice_number=_generate_invoice_number(db),
        subtotal=0.0,
        tax_amount=0.0,
        total_amount=0.0,
        profit=0.0,
        created_by=user_id,
    )
    db.add(db_invoice)
    db.flush()

    for item in items_data:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product {item.product_id} not found")

        cost_price = product.cost_price
        total_price = item.quantity * item.unit_price
        item_profit = (item.unit_price - cost_price) * item.quantity

        subtotal += total_price
        profit += item_profit

        db_item = SaleItem(
            invoice_id=db_invoice.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            cost_price=cost_price,
            total_price=total_price,
        )
        db.add(db_item)

        product.stock_quantity -= item.quantity

        movement = StockMovement(
            product_id=item.product_id,
            movement_type="SALE",
            quantity=-item.quantity,
            reference_id=db_invoice.id,
            reference_type="sale_invoice",
            notes=f"Sale invoice {db_invoice.invoice_number}",
            created_by=user_id,
        )
        db.add(movement)

    tax_amount = subtotal * settings.TAX_RATE if invoice.apply_tax else 0.0
    total_amount = subtotal + tax_amount

    db_invoice.subtotal = subtotal
    db_invoice.tax_amount = tax_amount
    db_invoice.total_amount = total_amount
    db_invoice.profit = profit

    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def update_sale_invoice(db: Session, invoice_id: int, invoice: SaleInvoiceUpdate) -> Optional[SaleInvoice]:
    db_invoice = get_sale_invoice(db, invoice_id)
    if not db_invoice:
        return None
    for field, value in invoice.model_dump(exclude_unset=True).items():
        setattr(db_invoice, field, value)
    db.commit()
    db.refresh(db_invoice)
    return db_invoice


def delete_sale_invoice(db: Session, invoice_id: int) -> bool:
    db_invoice = get_sale_invoice(db, invoice_id)
    if not db_invoice:
        return False
    db.delete(db_invoice)
    db.commit()
    return True
