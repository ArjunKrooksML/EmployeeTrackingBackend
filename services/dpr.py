from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import DPR, Project
from fastapi import HTTPException
from datetime import date
from typing import Optional


def all_projects(db: Session):
    return db.query(Project).order_by(Project.name).all()


def get_dprs(project_id: int, db: Session, skip: int = 0, limit: int = 20,
             month: Optional[int] = None, year: Optional[int] = None):
    if not db.query(Project).filter(Project.project_id == project_id).first():
        raise HTTPException(404, "Project not found")
    q = db.query(DPR).filter(DPR.project_id == project_id).order_by(DPR.date.desc())
    if month and year:
        q = q.filter(extract('month', DPR.date) == month, extract('year', DPR.date) == year)
    total = q.count()
    return total, q.offset(skip).limit(limit).all()


def create_dpr(project_id: int, d: date, mm16: int, mm20: int, mm25: int, mm32: int,
               forging_qty: int, uploaded_by: str, db: Session):
    if not db.query(Project).filter(Project.project_id == project_id).first():
        raise HTTPException(404, "Project not found")
    entry = DPR(project_id=project_id, date=d, mm16=mm16, mm20=mm20,
                mm25=mm25, mm32=mm32, forging_qty=forging_qty, uploaded_by=uploaded_by)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_dpr(entry_id: int, d: date, mm16: int, mm20: int, mm25: int, mm32: int,
               forging_qty: int, db: Session):
    entry = db.query(DPR).filter(DPR.id == entry_id).first()
    if not entry:
        raise HTTPException(404, "DPR entry not found")
    entry.date = d
    entry.mm16 = mm16
    entry.mm20 = mm20
    entry.mm25 = mm25
    entry.mm32 = mm32
    entry.forging_qty = forging_qty
    db.commit()
    db.refresh(entry)
    return entry


def set_forging(project_id: int, has_forging: bool, db: Session):
    proj = db.query(Project).filter(Project.project_id == project_id).first()
    if not proj:
        raise HTTPException(404, "Project not found")
    proj.has_forging = has_forging
    db.commit()
    db.refresh(proj)
    return proj
