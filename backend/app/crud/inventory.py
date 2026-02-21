from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.stock import StockMovement
from ..models.product import Product
from ..schemas.stock import StockAdjustment


def get_stock_movements(db: Session, skip: int = 0, limit: int = 100) -> List[StockMovement]:
    return db.query(StockMovement).order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()


def get_stock_movements_by_product(db: Session, product_id: int) -> List[StockMovement]:
    return db.query(StockMovement).filter(StockMovement.product_id == product_id).all()


def create_stock_adjustment(db: Session, adjustment: StockAdjustment, user_id: int) -> StockMovement:
    product = db.query(Product).filter(Product.id == adjustment.product_id).first()
    if not product:
        raise ValueError(f"Product {adjustment.product_id} not found")

    product.stock_quantity += adjustment.quantity

    movement = StockMovement(
        product_id=adjustment.product_id,
        movement_type="ADJUSTMENT",
        quantity=adjustment.quantity,
        notes=adjustment.notes,
        created_by=user_id,
    )
    db.add(movement)
    db.commit()
    db.refresh(movement)
    return movement


def get_stock_report(db: Session) -> List[dict]:
    products = db.query(Product).filter(Product.is_active == True).all()
    report = []
    for p in products:
        report.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "category": p.category,
            "unit": p.unit,
            "stock_quantity": p.stock_quantity,
            "min_stock_level": p.min_stock_level,
            "cost_price": p.cost_price,
            "selling_price": p.selling_price,
            "stock_value": p.stock_quantity * p.cost_price,
            "is_low_stock": p.stock_quantity <= p.min_stock_level,
        })
    return report
