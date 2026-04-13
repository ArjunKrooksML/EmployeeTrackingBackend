from sqlalchemy.orm import Session
from fastapi import HTTPException
from database.models import Leave as LeaveDB, Employee as EmployeeDB
from models.leaves import LeaveCreate
from typing import List, Optional

def request_leave(data: LeaveCreate, db: Session) -> LeaveDB:
    # Check if employee exists
    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == data.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Prevent duplicate leave request for same day
    existing = db.query(LeaveDB).filter(
        LeaveDB.employee_id == data.employee_id,
        LeaveDB.leave_date == data.leave_date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A leave request already exists for this date")

    # Ensure valid inputs
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
        return new_leave
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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
    base_q = db.query(LeaveDB, EmployeeDB.employee_name).join(
        EmployeeDB, LeaveDB.employee_id == EmployeeDB.employee_id
    )
    if status:
        base_q = base_q.filter(LeaveDB.status == status)
    total = base_q.count()
    results = base_q.order_by(LeaveDB.created_at.desc()).offset(skip).limit(limit).all()
    formatted = []
    for leave, emp_name in results:
        leave_dict = leave.__dict__.copy()
        leave_dict["employee_name"] = emp_name
        formatted.append(leave_dict)
    pages = (total + page_size - 1) // page_size if page_size else 1
    return {"items": formatted, "total": total, "page": page, "page_size": page_size, "pages": pages}

def update_leave_status(leave_id: int, new_status: str, db: Session) -> LeaveDB:
    if new_status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    leave = db.query(LeaveDB).filter(LeaveDB.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = new_status
    try:
        db.commit()
        db.refresh(leave)
        return leave
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
