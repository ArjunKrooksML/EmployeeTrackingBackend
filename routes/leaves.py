from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from models.leaves import LeaveCreate, LeaveResponse, LeaveUpdateStatus, AdminLeaveResponse
from services.leaves import request_leave, get_employee_leaves, get_all_leaves, update_leave_status
from middleware.rbac import require_gm, require_hr_or_gm

router = APIRouter(prefix="/leaves", tags=["Leaves"])

@router.post("/request", response_model=LeaveResponse)
def submit_leave_request(data: LeaveCreate, db: Session = Depends(get_db)):
    return request_leave(data, db)

@router.get("/employee/{emp_id}", response_model=List[LeaveResponse])
def fetch_employee_leaves(emp_id: int, db: Session = Depends(get_db)):
    return get_employee_leaves(emp_id, db)

@router.get("/all", response_model=List[AdminLeaveResponse], dependencies=[Depends(require_hr_or_gm)])
def fetch_all_leaves(db: Session = Depends(get_db)):
    """Admin route to fetch all leaves across the company"""
    return get_all_leaves(db)

@router.put("/{leave_id}/status", response_model=LeaveResponse, dependencies=[Depends(require_hr_or_gm)])
def change_leave_status(leave_id: int, update_data: LeaveUpdateStatus, db: Session = Depends(get_db)):
    """Admin route to approve or reject a leave request"""
    return update_leave_status(leave_id, update_data.status, db)
