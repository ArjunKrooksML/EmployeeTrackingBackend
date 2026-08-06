from sqlalchemy.orm import Session
from datetime import datetime, date, timezone, timedelta
from typing import Optional
from database.models import Attendance, Employee
from fastapi import HTTPException
from models.attendance import AttUpdate
import services.storage as storage

IST = timezone(timedelta(hours=5, minutes=30))

def do_checkin(emp_id: int, db: Session, lat: Optional[float] = None, lng: Optional[float] = None):
    # Employee already validated by auth middleware
    now_ist = datetime.now(IST)
    today = now_ist.date()
    now = now_ist.time()
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


def get_att(emp_id: int, db: Session, year: int = None):
    q = db.query(Attendance).filter(Attendance.employee_id == emp_id)
    if year:
        q = q.filter(Attendance.date >= date(year, 1, 1), Attendance.date <= date(year, 12, 31))
    return q.order_by(Attendance.date.desc()).all()


def all_att(db: Session, skip: int = 0, limit: int = 20, page: int = 1, page_size: int = 20):
    # Fetch all attendance joined with employee name
    base_q = db.query(Attendance, Employee.employee_name, Employee.profile_pic_path).join(
        Employee, Attendance.employee_id == Employee.employee_id
    )
    total = db.query(Attendance).count()
    rows = base_q.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
    out = []
    for att, name, pic_path in rows:
        d = {c.name: getattr(att, c.name) for c in att.__table__.columns}
        d['employee_name'] = name
        d['profile_pic_url'] = storage.signed_url(pic_path) if pic_path else None
        out.append(d)
    pages = (total + page_size - 1) // page_size if page_size else 1
    return {"items": out, "total": total, "page": page, "page_size": page_size, "pages": pages}


def upd_att(att_id: int, data: AttUpdate, db: Session):
    att = db.query(Attendance).filter(Attendance.id == att_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    if data.attendance not in ['present', 'absent', 'late']:
        raise HTTPException(status_code=400, detail="Invalid attendance status")
    status = data.attendance
    # If admin marks late but check-in is at or after 14:00, treat as absent (half-day)
    if status == 'late' and att.checkin and att.checkin.hour >= 14:
        status = 'absent'
    att.attendance = status
    db.commit()
    db.refresh(att)
    return att
