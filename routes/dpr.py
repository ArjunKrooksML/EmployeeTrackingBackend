from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.rbac import require_any_user
from models.dpr import DPRCreate, DPRResp
from models.pagination import PaginatedResponse
from services import dpr as svc

router = APIRouter(prefix="/dpr", tags=["dpr"])


def _name(user) -> str:
    return getattr(user, 'employee_name', None) or getattr(user, 'name', 'Unknown')


@router.get("/projects")
def list_projects(db: Session = Depends(get_db), _=Depends(require_any_user)):
    return svc.all_projects(db)


@router.get("/{project_id}", response_model=PaginatedResponse[DPRResp])
def get_dprs(
    project_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_any_user),
):
    skip = (page - 1) * page_size
    total, items = svc.get_dprs(project_id, db, skip=skip, limit=page_size)
    pages = max(1, (total + page_size - 1) // page_size)
    return {"total": total, "page": page, "page_size": page_size, "pages": pages, "items": items}


@router.post("/{project_id}", response_model=DPRResp)
def create_dpr(
    project_id: int,
    data: DPRCreate,
    db: Session = Depends(get_db),
    user=Depends(require_any_user),
):
    return svc.create_dpr(project_id, data.date, data.description, _name(user), db)
