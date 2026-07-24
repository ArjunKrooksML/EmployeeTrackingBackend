from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from database.connection import get_db
from middleware.rbac import require_any_user
from models.chasers import ChaserCreate, ChaserResp, StockBalanceResp
from models.pagination import PaginatedResponse
from services import chasers as svc

router = APIRouter(prefix="/chasers", tags=["chasers"])


def _name(user) -> str:
    return getattr(user, 'employee_name', None) or getattr(user, 'name', 'Unknown')


@router.get("/stock", response_model=StockBalanceResp)
def get_stock(db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.get_stock_balance(db)


@router.get("", response_model=PaginatedResponse[ChaserResp])
def get_chasers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=5000),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_any_user),
):
    skip = (page - 1) * page_size
    total, items = svc.get_chasers(db, skip=skip, limit=page_size, month=month, year=year)
    pages = max(1, (total + page_size - 1) // page_size)
    return {"total": total, "page": page, "page_size": page_size, "pages": pages, "items": items}


@router.post("", response_model=ChaserResp)
def create_chaser(data: ChaserCreate, db: Session = Depends(get_db), user=Depends(require_any_user)):
    return svc.create_chaser(data.model_dump(), _name(user), db)


@router.put("/{chaser_id}", response_model=ChaserResp)
def update_chaser(chaser_id: int, data: ChaserCreate, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.update_chaser(chaser_id, data.model_dump(), db)


@router.delete("/{chaser_id}")
def delete_chaser(chaser_id: int, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.delete_chaser(chaser_id, db)
