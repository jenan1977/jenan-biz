from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[Product]:
    return db.query(Product).filter(Product.sku == sku).first()


def get_products(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Product]:
    query = db.query(Product)
    if active_only:
        query = query.filter(Product.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_low_stock_products(db: Session) -> List[Product]:
    return (
        db.query(Product)
        .filter(Product.is_active == True, Product.stock_quantity <= Product.min_stock_level)
        .all()
    )


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate) -> Optional[Product]:
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    for field, value in product.model_dump(exclude_unset=True).items():
        setattr(db_product, field, value)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    db.delete(db_product)
    db.commit()
    return True
