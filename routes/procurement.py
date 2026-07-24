from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from middleware.rbac import require_any_user
from models.procurement import VendorCreate, VendorResp, ProcurementCreate, ProcurementResp
from models.pagination import PaginatedResponse
from services import procurement as svc

router = APIRouter(prefix="/factory", tags=["factory-procurement"])


def _name(user) -> str:
    return getattr(user, 'employee_name', None) or getattr(user, 'name', 'Unknown')


@router.get("/vendors", response_model=List[VendorResp])
def list_vendors(db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.list_vendors(db)


@router.post("/vendors", response_model=VendorResp)
def create_vendor(data: VendorCreate, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.create_vendor(data.name, db)


@router.put("/vendors/{vendor_id}", response_model=VendorResp)
def update_vendor(vendor_id: int, data: VendorCreate, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.update_vendor(vendor_id, data.name, db)


@router.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.delete_vendor(vendor_id, db)


@router.get("/procurement", response_model=PaginatedResponse[ProcurementResp])
def get_procurements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_any_user),
):
    skip = (page - 1) * page_size
    total, items = svc.get_procurements(db, skip=skip, limit=page_size, month=month, year=year)
    pages = max(1, (total + page_size - 1) // page_size)
    return {"total": total, "page": page, "page_size": page_size, "pages": pages, "items": items}


@router.post("/procurement", response_model=ProcurementResp)
def create_procurement(data: ProcurementCreate, db: Session = Depends(get_db), user=Depends(require_any_user)):
    return svc.create_procurement(data.model_dump(), _name(user), db)


@router.put("/procurement/{procurement_id}", response_model=ProcurementResp)
def update_procurement(procurement_id: int, data: ProcurementCreate, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.update_procurement(procurement_id, data.model_dump(), db)


@router.delete("/procurement/{procurement_id}")
def delete_procurement(procurement_id: int, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.delete_procurement(procurement_id, db)
