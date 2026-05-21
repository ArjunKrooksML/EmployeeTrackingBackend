from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from models.attendance import AttResp, AttWithEmp, AttUpdate, CheckinReq
from models.pagination import PaginatedResponse
from middleware.rbac import require_gm, require_hr_or_gm
from middleware.auth import get_current_employee
from database.models import Employee as EmpDB
from services import attendance as svc

router = APIRouter()


@router.post("/attendance/checkin", response_model=AttResp)
def checkin(data: CheckinReq, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    if data.employee_id != emp.employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot check in for another employee")
    return svc.do_checkin(data.employee_id, db, data.lat, data.lng)


@router.get("/attendance/employee/{employee_id}", response_model=List[AttResp])
def my_att(employee_id: int, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    if employee_id != emp.employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another employee's attendance")
    return svc.get_att(employee_id, db)


@router.get("/attendance/all", response_model=PaginatedResponse[AttWithEmp])
def att_all(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    db: Session = Depends(get_db),
    _: None = Depends(require_gm),
):
    skip = (page - 1) * page_size
    return svc.all_att(db, skip=skip, limit=page_size, page=page, page_size=page_size)


@router.put("/attendance/{att_id}", response_model=AttResp)
def upd_att(att_id: int, data: AttUpdate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return svc.upd_att(att_id, data, db)
