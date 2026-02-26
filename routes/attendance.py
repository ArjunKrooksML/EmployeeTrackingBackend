from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from models.attendance import AttendanceResponse, AttendanceWithEmployee, AttendanceUpdate
from services import attendance as attendance_service

router = APIRouter()

@router.post("/attendance/checkin", response_model=AttendanceResponse)
def check_in(employee_id: int = Query(..., description="Employee ID"), db: Session = Depends(get_db)):
    return attendance_service.check_in_employee(employee_id, db)

@router.get("/attendance/employee/{employee_id}", response_model=List[AttendanceResponse])
def get_my_attendance(employee_id: int, db: Session = Depends(get_db)):
    return attendance_service.get_employee_attendance(employee_id, db)

@router.get("/attendance/all", response_model=List[AttendanceWithEmployee])
def list_all_attendance(db: Session = Depends(get_db)):
    return attendance_service.get_all_attendance(db)

@router.put("/attendance/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, update_data: AttendanceUpdate, db: Session = Depends(get_db)):
    return attendance_service.update_attendance_status(attendance_id, update_data, db)

