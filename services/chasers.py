from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import Chaser, Project
from fastapi import HTTPException
from typing import Optional

SIZES = ['size_2_5', 'size_3', 'size_3_5', 'size_4']


def _project_name(project_id, db: Session):
    if not project_id:
        return None
    p = db.query(Project).filter(Project.project_id == project_id).first()
    return p.name if p else None


def _fmt(c: Chaser, db: Session) -> dict:
    return {
        "id": c.id, "date": c.date, "entry_type": c.entry_type, "vendor": c.vendor,
        "project_id": c.project_id, "project_name": _project_name(c.project_id, db),
        "size_2_5": c.size_2_5, "size_3": c.size_3, "size_3_5": c.size_3_5, "size_4": c.size_4,
        "description": c.description, "uploaded_by": c.uploaded_by, "created_at": c.created_at,
    }


def get_chasers(db: Session, skip: int = 0, limit: int = 20,
                 month: Optional[int] = None, year: Optional[int] = None):
    q = db.query(Chaser).order_by(Chaser.date.desc(), Chaser.id.desc())
    if month and year:
        q = q.filter(extract('month', Chaser.date) == month, extract('year', Chaser.date) == year)
    total = q.count()
    rows = q.offset(skip).limit(limit).all()
    return total, [_fmt(c, db) for c in rows]


def _compute_balance(db: Session, exclude_id: Optional[int] = None) -> dict:
    balance = {s: 0 for s in SIZES}
    q = db.query(Chaser)
    if exclude_id is not None:
        q = q.filter(Chaser.id != exclude_id)
    for c in q.all():
        sign = 1 if c.entry_type == 'stock' else -1
        for s in SIZES:
            balance[s] += sign * (getattr(c, s) or 0)
    return balance


def get_stock_balance(db: Session) -> dict:
    return _compute_balance(db)


def _validate_sufficient_stock(data: dict, db: Session, exclude_id: Optional[int] = None):
    balance = _compute_balance(db, exclude_id)
    short = [s for s in SIZES if (data.get(s) or 0) > balance[s]]
    if short:
        details = ', '.join(f"{s[5:].replace('_', '.')} (have {balance[s]}, need {data.get(s) or 0})" for s in short)
        raise HTTPException(400, f"Insufficient chaser stock — {details}")


def create_chaser(data: dict, uploaded_by: str, db: Session) -> dict:
    if data.get('entry_type', 'issue') == 'issue':
        if not data.get('project_id'):
            raise HTTPException(400, "Site is required for a site issue entry")
        if not db.query(Project).filter(Project.project_id == data["project_id"]).first():
            raise HTTPException(404, "Project not found")
        _validate_sufficient_stock(data, db)
    else:
        data['project_id'] = None
    c = Chaser(uploaded_by=uploaded_by, **data)
    db.add(c)
    db.commit()
    db.refresh(c)
    return _fmt(c, db)


def update_chaser(chaser_id: int, data: dict, db: Session) -> dict:
    c = db.query(Chaser).filter(Chaser.id == chaser_id).first()
    if not c:
        raise HTTPException(404, "Chaser entry not found")
    if data.get('entry_type', 'issue') == 'issue':
        if not data.get('project_id'):
            raise HTTPException(400, "Site is required for a site issue entry")
        if not db.query(Project).filter(Project.project_id == data["project_id"]).first():
            raise HTTPException(404, "Project not found")
        _validate_sufficient_stock(data, db, exclude_id=chaser_id)
    else:
        data['project_id'] = None
    for k, v in data.items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return _fmt(c, db)


def delete_chaser(chaser_id: int, db: Session) -> dict:
    c = db.query(Chaser).filter(Chaser.id == chaser_id).first()
    if not c:
        raise HTTPException(404, "Chaser entry not found")
    db.delete(c)
    db.commit()
    return {"message": "Chaser entry deleted"}
