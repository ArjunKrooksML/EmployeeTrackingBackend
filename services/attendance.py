from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from database.models import Attendance, Employee
from fastapi import HTTPException
from models.attendance import AttendanceUpdate

def check_in_employee(employee_id: int, db: Session):
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with ID {employee_id} not found")
    
    today = date.today()
    now_time = datetime.now().time()
    
    existing = db.query(Attendance).filter(
        Attendance.employee_id == employee_id,
        Attendance.date == today
    ).first()
    
    if existing:
        return existing
    
    new_attendance = Attendance(
        employee_id=employee_id,
        date=today,
        checkin=now_time,
        attendance='absent'  # Set to 'absent' initially (pending approval), admin will approve to 'present'
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance

def get_employee_attendance(employee_id: int, db: Session):
    return db.query(Attendance).filter(Attendance.employee_id == employee_id).order_by(Attendance.date.desc()).all()

def get_all_attendance(db: Session):
    results = db.query(Attendance, Employee.employee_name).join(
        Employee, Attendance.employee_id == Employee.employee_id
    ).order_by(Attendance.date.desc()).all()
    
    out = []
    for att, name in results:
        # Create a dict from the model, excluding SQLAlchemy internal state
        att_dict = {c.name: getattr(att, c.name) for c in att.__table__.columns}
        att_dict['employee_name'] = name
        out.append(att_dict)
    return out

def update_attendance_status(attendance_id: int, update_data: AttendanceUpdate, db: Session):
    att = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    if update_data.attendance not in ['present', 'absent', 'late']:
        raise HTTPException(status_code=400, detail="Invalid attendance status")
        
    att.attendance = update_data.attendance
    db.commit()
    db.refresh(att)
    return att

