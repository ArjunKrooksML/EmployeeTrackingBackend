from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import Optional
from database.models import Attendance, Employee
from fastapi import HTTPException
from models.attendance import AttUpdate


def do_checkin(emp_id: int, db: Session, lat: Optional[float] = None, lng: Optional[float] = None):
    # Verify employee exists
    emp = db.query(Employee).filter(Employee.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee {emp_id} not found")
    today = date.today()
    now = datetime.now().time()
    # Return existing record if already checked in today
    rec = db.query(Attendance).filter(
        Attendance.employee_id == emp_id,
        Attendance.date == today
    ).first()
    if rec:
        return rec
    # Create new attendance record with location
    att = Attendance(
        employee_id=emp_id,
        date=today,
        checkin=now,
        attendance='pending',
        lat=lat,
        lng=lng
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


def get_att(emp_id: int, db: Session):
    # Fetch all attendance for one employee, newest first
    return db.query(Attendance).filter(
        Attendance.employee_id == emp_id
    ).order_by(Attendance.date.desc()).all()


def all_att(db: Session):
    # Fetch all attendance joined with employee name
    rows = db.query(Attendance, Employee.employee_name).join(
        Employee, Attendance.employee_id == Employee.employee_id
    ).order_by(Attendance.date.desc()).all()
    out = []
    for att, name in rows:
        d = {c.name: getattr(att, c.name) for c in att.__table__.columns}
        d['employee_name'] = name
        out.append(d)
    return out


def upd_att(att_id: int, data: AttUpdate, db: Session):
    # Update status of a specific attendance record
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    if data.attendance not in ['present', 'absent', 'late']:
        raise HTTPException(status_code=400, detail="Invalid attendance status")
    att.attendance = data.attendance
    db.commit()
    db.refresh(att)
    return att
