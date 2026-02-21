from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.stock import Stock, StockMovement


class InventoryService:

    @staticmethod
    def get_or_create_stock(db: Session, product_id: int) -> Stock:
        stock = db.query(Stock).filter(Stock.product_id == product_id).first()
        if not stock:
            stock = Stock(product_id=product_id, current_quantity=0.0)
            db.add(stock)
            db.flush()
        return stock

    @staticmethod
    def update_stock_in(db: Session, product_id: int, quantity: float, ref_type: str, ref_id: int):
        stock = InventoryService.get_or_create_stock(db, product_id)
        stock.current_quantity += quantity
        movement = StockMovement(
            product_id=product_id,
            movement_type="IN",
            quantity=quantity,
            reference_type=ref_type,
            reference_id=ref_id,
        )
        db.add(movement)

    @staticmethod
    def update_stock_out(db: Session, product_id: int, quantity: float, ref_type: str, ref_id: int):
        stock = InventoryService.get_or_create_stock(db, product_id)
        if stock.current_quantity < quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product_id={product_id}")
        stock.current_quantity -= quantity
        movement = StockMovement(
            product_id=product_id,
            movement_type="OUT",
            quantity=quantity,
            reference_type=ref_type,
            reference_id=ref_id,
        )
        db.add(movement)

    @staticmethod
    def adjust_stock(db: Session, product_id: int, quantity: float, notes: str = None):
        stock = InventoryService.get_or_create_stock(db, product_id)
        stock.current_quantity = quantity
        movement = StockMovement(
            product_id=product_id,
            movement_type="ADJUSTMENT",
            quantity=quantity,
            reference_type="adjustment",
            notes=notes,
        )
        db.add(movement)
