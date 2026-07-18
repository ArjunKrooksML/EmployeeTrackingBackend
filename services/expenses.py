import uuid, json, asyncio
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Expense, Employee
import services.storage as storage
from datetime import date
from typing import Optional, List


def _parse_atts(path: Optional[str], name: Optional[str]) -> list:
    if not path:
        return []
    try:
        parsed = json.loads(path)
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    # old single-file format
    return [{"path": path, "name": name or path.split('/')[-1]}]


def _total(e: Expense) -> int:
    items = e.items if isinstance(e.items, list) else []
    return round(sum(float(i.get("amount", 0)) for i in items))


def _fmt(e: Expense, emp_name: Optional[str]) -> dict:
    atts = _parse_atts(e.attachment_path, e.attachment_name)
    total = _total(e)
    return {
        "id": e.id,
        "employee_id": e.employee_id,
        "employee_name": emp_name,
        "title": e.title,
        "date": e.date.isoformat() if e.date else None,
        "date_to": e.date_to.isoformat() if e.date_to else None,
        "items": e.items if isinstance(e.items, list) else [],
        "attachments": [{"url": storage.signed_url(a["path"]), "name": a["name"]} for a in atts],
        "status": e.status,
        "paid": e.paid,
        "paid_amount": e.paid_amount,
        "balance": total - e.paid_amount,
        "remarks": e.remarks,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


def _get_name(employee_id: int, db: Session) -> Optional[str]:
    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    return emp.employee_name if emp else None


async def _upload_files(employee_id: int, file_data: List[tuple]) -> list:
    async def _upload(filename: str, data: bytes, content_type: str) -> dict:
        path = f"expenses/{employee_id}/{uuid.uuid4().hex}_{filename}"
        await asyncio.to_thread(storage.upload, path, data, content_type)
        return {"path": path, "name": filename}

    return list(await asyncio.gather(*(_upload(fn, data, ct) for fn, data, ct in file_data))) if file_data else []


async def create(employee_id: int, title: str, d: date, items: list,
                  file_data: List[tuple], date_to: Optional[date], db: Session) -> dict:
    atts = await _upload_files(employee_id, file_data)
    att_json = json.dumps(atts) if atts else None
    exp = Expense(employee_id=employee_id, title=title, date=d, date_to=date_to,
                  items=items, attachment_path=att_json, attachment_name=None)
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _fmt(exp, _get_name(employee_id, db))


async def update_expense(expense_id: int, employee_id: int, title: Optional[str], d: Optional[date],
                          items: Optional[list], date_to: Optional[date], clear_date_to: bool,
                          file_data: List[tuple], db: Session) -> dict:
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e or e.employee_id != employee_id:
        raise HTTPException(404, "Not found")
    if e.status != 'pending':
        raise HTTPException(400, "Only pending expenses can be edited")
    if title is not None:
        e.title = title
    if d is not None:
        e.date = d
    if items is not None:
        e.items = items
    if clear_date_to:
        e.date_to = None
    elif date_to is not None:
        e.date_to = date_to
    if file_data:
        new_atts = await _upload_files(employee_id, file_data)
        existing = _parse_atts(e.attachment_path, e.attachment_name)
        e.attachment_path = json.dumps(existing + new_atts)
    db.commit()
    db.refresh(e)
    return _fmt(e, _get_name(employee_id, db))


def delete_expense(expense_id: int, employee_id: int, db: Session) -> dict:
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e or e.employee_id != employee_id:
        raise HTTPException(404, "Not found")
    if e.status != 'pending':
        raise HTTPException(400, "Only pending expenses can be deleted")
    for a in _parse_atts(e.attachment_path, e.attachment_name):
        try:
            storage.delete(a["path"])
        except Exception:
            pass
    db.delete(e)
    db.commit()
    return {"message": "Expense deleted"}


def my(employee_id: int, db: Session) -> list:
    rows = db.query(Expense).filter(Expense.employee_id == employee_id).order_by(Expense.date.desc()).all()
    if not rows:
        return []
    name = _get_name(employee_id, db)
    return [_fmt(e, name) for e in rows]


def all_expenses(db: Session, skip: int, limit: int, status: Optional[str] = None):
    q = db.query(Expense).order_by(Expense.created_at.desc())
    if status:
        q = q.filter(Expense.status == status)
    total = q.count()
    rows = q.offset(skip).limit(limit).all()
    if not rows:
        return total, []
    emp_ids = {e.employee_id for e in rows}
    names = {emp.employee_id: emp.employee_name for emp in db.query(Employee).filter(Employee.employee_id.in_(emp_ids)).all()}
    return total, [_fmt(e, names.get(e.employee_id)) for e in rows]


def get_one(expense_id: int, db: Session) -> dict:
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Not found")
    return _fmt(e, _get_name(e.employee_id, db))


def record_payment(expense_id: int, amount: int, remarks: Optional[str], db: Session, employee_id: Optional[int] = None) -> dict:
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Not found")
    if employee_id is not None and e.employee_id != employee_id:
        raise HTTPException(404, "Not found")
    if e.status != 'approved':
        raise HTTPException(400, "Only approved expenses can receive payments")
    balance = _total(e) - e.paid_amount
    if amount <= 0:
        raise HTTPException(400, "Payment amount must be positive")
    if amount > balance:
        raise HTTPException(400, f"Payment exceeds remaining balance of {balance}")
    e.paid_amount += amount
    if remarks:
        e.remarks = remarks
    db.commit()
    db.refresh(e)
    return _fmt(e, _get_name(e.employee_id, db))


def mark_paid(expense_id: int, remarks: Optional[str], db: Session) -> dict:
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Not found")
    if e.status != 'approved':
        raise HTTPException(400, "Only approved expenses can be marked as paid")
    e.paid = True
    e.paid_amount = _total(e)
    if remarks:
        e.remarks = remarks
    db.commit()
    db.refresh(e)
    return _fmt(e, _get_name(e.employee_id, db))


def review(expense_id: int, status: str, remarks: Optional[str], db: Session) -> dict:
    if status not in ('approved', 'rejected'):
        raise HTTPException(400, "status must be approved or rejected")
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(404, "Not found")
    e.status = status
    if remarks:
        e.remarks = remarks
    db.commit()
    db.refresh(e)
    return _fmt(e, _get_name(e.employee_id, db))
