from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.stock import StockMovementResponse, StockAdjustment
from ..crud import inventory as crud
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/movements", response_model=List[StockMovementResponse])
def list_movements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud.get_stock_movements(db, skip=skip, limit=limit)


@router.get("/stock-report")
def stock_report(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return crud.get_stock_report(db)


@router.post("/adjustment", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
def stock_adjustment(
    adjustment: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    try:
        return crud.create_stock_adjustment(db, adjustment, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
