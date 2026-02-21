from typing import List, Optional
from sqlalchemy.orm import Session

from ..models.supplier import Supplier
from ..schemas.supplier import SupplierCreate, SupplierUpdate


def get_supplier(db: Session, supplier_id: int) -> Optional[Supplier]:
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def get_suppliers(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Supplier]:
    query = db.query(Supplier)
    if active_only:
        query = query.filter(Supplier.is_active == True)
    return query.offset(skip).limit(limit).all()


def create_supplier(db: Session, supplier: SupplierCreate) -> Supplier:
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def update_supplier(db: Session, supplier_id: int, supplier: SupplierUpdate) -> Optional[Supplier]:
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        return None
    for field, value in supplier.model_dump(exclude_unset=True).items():
        setattr(db_supplier, field, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def delete_supplier(db: Session, supplier_id: int) -> bool:
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        return False
    db.delete(db_supplier)
    db.commit()
    return True
