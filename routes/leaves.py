from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from models.leaves import LeaveCreate, LeaveResponse, LeaveUpdateStatus, AdminLeaveResponse
from models.pagination import PaginatedResponse
from services.leaves import request_leave, get_employee_leaves, get_all_leaves, update_leave_status, cancel_leave
from services.email import send_leave_status_email
from services.whatsapp import send_leave_status_whatsapp
from middleware.rbac import require_hr_or_gm
from middleware.auth import get_current_employee
from database.models import Employee as EmpDB

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("/request", response_model=LeaveResponse)
def submit_leave_request(data: LeaveCreate, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    data.employee_id = emp.employee_id
    return request_leave(data, db)


@router.get("/my", response_model=List[LeaveResponse])
def fetch_my_leaves(emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return get_employee_leaves(emp.employee_id, db)


@router.get("/all", response_model=PaginatedResponse[AdminLeaveResponse], dependencies=[Depends(require_hr_or_gm)])
def fetch_all_leaves(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    skip = (page - 1) * page_size
    return get_all_leaves(db, skip=skip, limit=page_size, page=page, page_size=page_size, status=status)


@router.put("/{leave_id}/status", response_model=LeaveResponse, dependencies=[Depends(require_hr_or_gm)])
def change_leave_status(leave_id: int, update_data: LeaveUpdateStatus, bg: BackgroundTasks, db: Session = Depends(get_db)):
    leave, notif = update_leave_status(leave_id, update_data.status, db)
    if notif:
        bg.add_task(send_leave_status_email, notif['email'], notif['name'], notif['status'], notif['leave_date'], notif['leave_type'], notif['day_type'], notif['reason'])
        if notif['phone']:
            bg.add_task(send_leave_status_whatsapp, notif['phone'], notif['name'], notif['status'], notif['leave_date'], notif['leave_type'], notif['reason'])
    return leave


@router.delete("/{leave_id}")
def cancel_leave_request(leave_id: int, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return cancel_leave(leave_id, emp.employee_id, db)
