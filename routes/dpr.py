from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from database.connection import get_db
from middleware.rbac import require_any_user
from models.dpr import DPRCreate, DPRUpdate, DPRResp, FactoryDPRCreate, FactoryDPRUpdate, FactoryDPRResp
from models.pagination import PaginatedResponse
from services import dpr as svc

router = APIRouter(prefix="/dpr", tags=["dpr"])


def _name(user) -> str:
    return getattr(user, 'employee_name', None) or getattr(user, 'name', 'Unknown')


@router.get("/projects")
def list_projects(db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.all_projects(db)


@router.get("/factory", response_model=PaginatedResponse[FactoryDPRResp])
def get_factory_dprs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_any_user),
):
    skip = (page - 1) * page_size
    total, items = svc.get_factory_dprs(db, skip=skip, limit=page_size, month=month, year=year)
    pages = max(1, (total + page_size - 1) // page_size)
    return {"total": total, "page": page, "page_size": page_size, "pages": pages, "items": items}


@router.post("/factory", response_model=FactoryDPRResp)
def create_factory_dpr(data: FactoryDPRCreate, db: Session = Depends(get_db), user=Depends(require_any_user)):
    return svc.create_factory_dpr(data.model_dump(), _name(user), db)


@router.put("/factory/{entry_id}", response_model=FactoryDPRResp)
def update_factory_dpr(entry_id: int, data: FactoryDPRUpdate, db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.update_factory_dpr(entry_id, data.model_dump(), db)


@router.get("/{project_id}", response_model=PaginatedResponse[DPRResp])
def get_dprs(
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    month: Optional[int] = Query(None),
    year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_any_user),
):
    skip = (page - 1) * page_size
    total, items = svc.get_dprs(project_id, db, skip=skip, limit=page_size, month=month, year=year)
    pages = max(1, (total + page_size - 1) // page_size)
    return {"total": total, "page": page, "page_size": page_size, "pages": pages, "items": items}


@router.post("/{project_id}", response_model=DPRResp)
def create_dpr(project_id: int, data: DPRCreate,
               db: Session = Depends(get_db), user=Depends(require_any_user)):
    return svc.create_dpr(project_id, data.date, data.mm16, data.mm20, data.mm25, data.mm28,
                          data.mm32, data.mm40, data.operator_name, data.description, _name(user), db)


@router.put("/{entry_id}", response_model=DPRResp)
def update_dpr(entry_id: int, data: DPRUpdate,
               db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.update_dpr(entry_id, data.date, data.mm16, data.mm20, data.mm25, data.mm28,
                          data.mm32, data.mm40, data.operator_name, data.description, db)
