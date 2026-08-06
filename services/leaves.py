from sqlalchemy.orm import Session
from sqlalchemy import extract
from fastapi import HTTPException
from database.models import Leave as LeaveDB, Employee as EmployeeDB, Attendance as AttendanceDB, Admin as AdminDB
from models.leaves import LeaveCreate
from services.email import send_leave_applied_email
import services.storage as storage
from typing import List, Optional, Tuple


def _notify_admins(leave: LeaveDB, emp_name: str, db: Session):
    admins = db.query(AdminDB).all()
    for admin in admins:
        try:
            send_leave_applied_email(admin.email, admin.name, emp_name, leave.leave_type, str(leave.leave_date), leave.day_type, leave.reason)
        except Exception as e:
            print(f"[email] Failed to send leave notification to {admin.email}: {e}")


def request_leave(data: LeaveCreate, db: Session) -> LeaveDB:
    # employee_id already validated by auth middleware — skip re-query
    existing = db.query(LeaveDB).filter(
        LeaveDB.employee_id == data.employee_id,
        LeaveDB.leave_date == data.leave_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A leave request already exists for this date")

    if data.leave_type == "casual":
        month, year = data.leave_date.month, data.leave_date.year
        if db.query(LeaveDB).filter(
            LeaveDB.employee_id == data.employee_id,
            LeaveDB.leave_type == "casual",
            LeaveDB.status != "rejected",
            extract("month", LeaveDB.leave_date) == month,
            extract("year", LeaveDB.leave_date) == year,
        ).count() >= 1:
            raise HTTPException(status_code=400, detail="Casual leave limit reached: only 1 casual leave allowed per month")

    if data.leave_type not in ["casual", "sick", "emergency"]:
        raise HTTPException(status_code=400, detail="Invalid leave_type. Must be 'casual', 'sick', or 'emergency'")
    if data.day_type not in ["full", "first_half", "second_half"]:
        raise HTTPException(status_code=400, detail="Invalid day_type. Must be 'full', 'first_half', or 'second_half'")

    new_leave = LeaveDB(
        employee_id=data.employee_id,
        leave_type=data.leave_type,
        leave_date=data.leave_date,
        day_type=data.day_type,
        reason=data.reason,
        status="pending"
    )
    try:
        db.add(new_leave)
        db.commit()
        db.refresh(new_leave)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == data.employee_id).first()
    _notify_admins(new_leave, emp.employee_name if emp else f"Employee #{data.employee_id}", db)
    return new_leave


def get_employee_leaves(emp_id: int, db: Session) -> List[LeaveDB]:
    return db.query(LeaveDB).filter(LeaveDB.employee_id == emp_id).order_by(LeaveDB.leave_date.desc()).all()


def get_all_leaves(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
) -> dict:
    q = db.query(LeaveDB, EmployeeDB.employee_name, EmployeeDB.profile_pic_path).join(
        EmployeeDB, LeaveDB.employee_id == EmployeeDB.employee_id
    )
    if status:
        q = q.filter(LeaveDB.status == status)
    total = q.count()
    rows = q.order_by(LeaveDB.created_at.desc()).offset(skip).limit(limit).all()
    items = []
    for leave, emp_name, pic_path in rows:
        d = leave.__dict__.copy()
        d['employee_name'] = emp_name
        d['profile_pic_url'] = storage.signed_url(pic_path) if pic_path else None
        items.append(d)
    pages = (total + page_size - 1) // page_size if page_size else 1
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}


def update_leave_status(leave_id: int, new_status: str, db: Session) -> Tuple[LeaveDB, Optional[dict]]:
    if new_status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    leave = db.query(LeaveDB).filter(LeaveDB.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    prev_status = leave.status
    leave.status = new_status

    if new_status == "approved":
        if not db.query(AttendanceDB).filter(
            AttendanceDB.employee_id == leave.employee_id,
            AttendanceDB.date == leave.leave_date
        ).first():
            db.add(AttendanceDB(employee_id=leave.employee_id, date=leave.leave_date, attendance="absent"))
    elif prev_status == "approved":
        att = db.query(AttendanceDB).filter(
            AttendanceDB.employee_id == leave.employee_id,
            AttendanceDB.date == leave.leave_date,
            AttendanceDB.attendance == "absent",
            AttendanceDB.checkin == None
        ).first()
        if att:
            db.delete(att)

    try:
        db.commit()
        db.refresh(leave)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # Fetch employee info for notification only when needed; caller handles sending
    notif = None
    if new_status in ("approved", "rejected"):
        emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == leave.employee_id).first()
        if emp:
            notif = {
                'email': emp.email,
                'phone': emp.phone_no,
                'name': emp.employee_name,
                'status': new_status,
                'leave_date': str(leave.leave_date),
                'leave_type': leave.leave_type,
                'day_type': leave.day_type,
                'reason': leave.reason,
            }

    return leave, notif


def cancel_leave(leave_id: int, employee_id: int, db: Session) -> dict:
    leave = db.query(LeaveDB).filter(LeaveDB.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if leave.employee_id != employee_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if leave.status == "rejected":
        raise HTTPException(status_code=400, detail="Cannot cancel a rejected leave")

    was_approved = leave.status == "approved"
    leave_date = leave.leave_date

    try:
        db.delete(leave)
        if was_approved:
            att = db.query(AttendanceDB).filter(
                AttendanceDB.employee_id == employee_id,
                AttendanceDB.date == leave_date,
                AttendanceDB.attendance == "absent",
                AttendanceDB.checkin == None
            ).first()
            if att:
                db.delete(att)
        db.commit()
        return {"message": "Leave cancelled"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
