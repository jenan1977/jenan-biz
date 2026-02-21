from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models.stock import Stock, StockMovement
from app.models.product import Product
from app.schemas.stock_schema import StockMovementOut, StockAdjustment
from app.auth.utils import get_current_active_user
from app.models.user import User
from app.services.inventory_service import InventoryService

router = APIRouter()


@router.get("/")
def get_all_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    stocks = db.query(Stock).options(joinedload(Stock.product)).all()
    return [
        {
            "id": s.id,
            "product_id": s.product_id,
            "current_quantity": s.current_quantity,
            "last_updated": s.last_updated,
            "product_name": s.product.name if s.product else None,
            "product_sku": s.product.sku if s.product else None,
            "min_stock": s.product.min_stock if s.product else None,
        }
        for s in stocks
    ]


@router.get("/low-stock")
def get_low_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    stocks = db.query(Stock).options(joinedload(Stock.product)).all()
    return [
        {
            "id": s.id,
            "product_id": s.product_id,
            "current_quantity": s.current_quantity,
            "product_name": s.product.name if s.product else None,
            "min_stock": s.product.min_stock if s.product else None,
        }
        for s in stocks
        if s.product and s.current_quantity <= s.product.min_stock
    ]


@router.get("/movements", response_model=List[StockMovementOut])
def get_all_movements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(StockMovement).order_by(StockMovement.created_at.desc()).all()


@router.post("/adjust")
def adjust_stock(
    data: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    product = db.query(Product).filter(Product.id == data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    InventoryService.adjust_stock(db, data.product_id, data.quantity, data.notes)
    db.commit()
    return {"message": "Stock adjusted successfully"}


@router.get("/movements/{product_id}", response_model=List[StockMovementOut])
def get_product_movements(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return (
        db.query(StockMovement)
        .filter(StockMovement.product_id == product_id)
        .order_by(StockMovement.created_at.desc())
        .all()
    )
