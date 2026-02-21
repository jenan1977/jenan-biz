from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.purchase import PurchaseInvoice
from app.models.invoice import Invoice
from app.models.stock import Stock
from app.auth.utils import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    total_products = db.query(func.count(Product.id)).scalar()
    total_suppliers = db.query(func.count(Supplier.id)).scalar()
    total_customers = db.query(func.count(Customer.id)).scalar()
    total_sales_invoices = db.query(func.count(Invoice.id)).scalar()
    total_purchase_invoices = db.query(func.count(PurchaseInvoice.id)).scalar()

    low_stock_count = (
        db.query(func.count(Stock.id))
        .join(Product, Stock.product_id == Product.id)
        .filter(Stock.current_quantity <= Product.min_stock)
        .scalar()
    )

    total_revenue = db.query(func.sum(Invoice.grand_total)).scalar() or 0.0
    total_profit = db.query(func.sum(Invoice.profit_amount)).scalar() or 0.0

    return {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_customers": total_customers,
        "total_sales_invoices": total_sales_invoices,
        "total_purchase_invoices": total_purchase_invoices,
        "low_stock_count": low_stock_count,
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
    }
