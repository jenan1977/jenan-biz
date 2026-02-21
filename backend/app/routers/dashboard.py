from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.user import User
from ..models.product import Product
from ..models.purchase import PurchaseInvoice
from ..models.sale import SaleInvoice
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    today = date.today()

    today_sales = db.query(func.coalesce(func.sum(SaleInvoice.total_amount), 0.0)).filter(
        SaleInvoice.date == today
    ).scalar()

    today_purchases = db.query(func.coalesce(func.sum(PurchaseInvoice.total_amount), 0.0)).filter(
        PurchaseInvoice.date == today
    ).scalar()

    total_products = db.query(func.count(Product.id)).filter(Product.is_active == True).scalar()

    low_stock_count = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.stock_quantity <= Product.min_stock_level,
    ).scalar()

    recent_sales = (
        db.query(SaleInvoice)
        .order_by(SaleInvoice.created_at.desc())
        .limit(5)
        .all()
    )

    recent_purchases = (
        db.query(PurchaseInvoice)
        .order_by(PurchaseInvoice.created_at.desc())
        .limit(5)
        .all()
    )

    recent_transactions = []
    for s in recent_sales:
        recent_transactions.append({
            "type": "sale",
            "invoice_number": s.invoice_number,
            "amount": s.total_amount,
            "date": str(s.date),
            "status": s.status,
        })
    for p in recent_purchases:
        recent_transactions.append({
            "type": "purchase",
            "invoice_number": p.invoice_number,
            "amount": p.total_amount,
            "date": str(p.date),
            "status": p.status,
        })

    recent_transactions.sort(key=lambda x: x["date"], reverse=True)

    return {
        "today_sales": float(today_sales),
        "today_purchases": float(today_purchases),
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "recent_transactions": recent_transactions[:10],
    }
