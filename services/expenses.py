import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import Expense, Employee
import services.storage as storage
from datetime import date
from typing import Optional


def _fmt(e: Expense, db: Session) -> dict:
    emp = db.query(Employee).filter(Employee.employee_id == e.employee_id).first()
    items = e.items if isinstance(e.items, list) else []
    return {
        "id": e.id,
        "employee_id": e.employee_id,
        "employee_name": emp.employee_name if emp else None,
        "title": e.title,
        "date": e.date.isoformat() if e.date else None,
        "items": items,
        "attachment_url": storage.signed_url(e.attachment_path) if e.attachment_path else None,
        "attachment_name": e.attachment_name,
        "status": e.status,
        "remarks": e.remarks,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


def create(employee_id: int, title: str, d: date, items: list, file: Optional[UploadFile], db: Session) -> dict:
    path = name = None
    if file and file.filename:
        data = file.file.read()
        path = f"expenses/{employee_id}/{uuid.uuid4().hex}_{file.filename}"
        storage.upload(path, data, file.content_type or 'application/octet-stream')
        name = file.filename
    exp = Expense(employee_id=employee_id, title=title, date=d, items=items,
                  attachment_path=path, attachment_name=name)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _fmt(exp, db)


def my(employee_id: int, db: Session) -> list:
    rows = db.query(Expense).filter(Expense.employee_id == employee_id).order_by(Expense.date.desc()).all()
    return [_fmt(e, db) for e in rows]


def all_expenses(db: Session, skip: int, limit: int, status: Optional[str] = None):
    q = db.query(Expense).order_by(Expense.date.desc())
    if status:
        q = q.filter(Expense.status == status)
    total = q.count()
    return total, [_fmt(e, db) for e in q.offset(skip).limit(limit).all()]


def get_one(expense_id: int, db: Session) -> dict:
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Not found")
    return _fmt(e, db)


def review(expense_id: int, status: str, remarks: Optional[str], db: Session) -> dict:
    if status not in ('approved', 'rejected'):
        raise HTTPException(400, "status must be approved or rejected")
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Not found")
    e.status = status
    e.remarks = remarks
    db.commit()
    db.refresh(e)
    return _fmt(e, db)
