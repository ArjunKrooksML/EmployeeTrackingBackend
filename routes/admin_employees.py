from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.connection import get_db
from middleware.rbac import require_hr_or_gm
from services.admin_employees import add_emp, get_all, get_by_id, update_emp, delete_emp, import_emps
from models.employees import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeImport
from models.pagination import PaginatedResponse

router = APIRouter(prefix="/admin/employees", tags=["admin/employees"])


class ImportReq(BaseModel):
    employees: List[EmployeeImport]


@router.get("", response_model=PaginatedResponse[EmployeeResponse])
async def list_emps(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    db: Session = Depends(get_db),
    _=Depends(require_hr_or_gm),
):
    skip = (page - 1) * page_size
    return get_all(db, skip=skip, limit=page_size, page=page, page_size=page_size)


@router.get("/{emp_id}", response_model=EmployeeResponse)
async def get_emp(emp_id: int, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    emp = get_by_id(emp_id, db)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.post("/create", response_model=EmployeeResponse)
async def create_emp(data: EmployeeCreate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return add_emp(data, db)


@router.put("/{emp_id}", response_model=EmployeeResponse)
async def update_emp_route(emp_id: int, data: EmployeeUpdate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    emp = update_emp(emp_id, data, db)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.delete("/{emp_id}")
async def delete_emp_route(emp_id: int, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    if not delete_emp(emp_id, db):
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}


@router.post("/import", response_model=List[EmployeeResponse])
async def import_route(req: ImportReq, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return import_emps(req.employees, db)
