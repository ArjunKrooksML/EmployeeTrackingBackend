from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from models.leaves import LeaveCreate, LeaveResponse, LeaveUpdateStatus, AdminLeaveResponse
from models.pagination import PaginatedResponse
from services.leaves import request_leave, get_employee_leaves, get_all_leaves, update_leave_status
from middleware.rbac import require_gm, require_hr_or_gm

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("/request", response_model=LeaveResponse)
def submit_leave_request(data: LeaveCreate, db: Session = Depends(get_db)):
    return request_leave(data, db)


@router.get("/employee/{emp_id}", response_model=List[LeaveResponse])
def fetch_employee_leaves(emp_id: int, db: Session = Depends(get_db)):
    return get_employee_leaves(emp_id, db)


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
def change_leave_status(leave_id: int, update_data: LeaveUpdateStatus, db: Session = Depends(get_db)):
    return update_leave_status(leave_id, update_data.status, db)
