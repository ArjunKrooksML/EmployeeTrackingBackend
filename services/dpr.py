from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import DPR, Project, FactoryDPR
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


def create_dpr(project_id: int, d: date, mm16: int, mm20: int, mm25: int, mm28: int, mm32: int, mm40: int,
               operator_name: str, description: str, uploaded_by: str, db: Session):
    if not db.query(Project).filter(Project.project_id == project_id).first():
        raise HTTPException(404, "Project not found")
    entry = DPR(project_id=project_id, date=d, mm16=mm16, mm20=mm20, mm25=mm25, mm28=mm28,
                mm32=mm32, mm40=mm40, operator_name=operator_name,
                description=description, uploaded_by=uploaded_by)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_dpr(entry_id: int, d: date, mm16: int, mm20: int, mm25: int, mm28: int, mm32: int, mm40: int,
               operator_name: str, description: str, db: Session):
    entry = db.query(DPR).filter(DPR.id == entry_id).first()
    if not entry:
        raise HTTPException(404, "DPR entry not found")
    entry.date = d
    entry.mm16 = mm16
    entry.mm20 = mm20
    entry.mm25 = mm25
    entry.mm28 = mm28
    entry.mm32 = mm32
    entry.mm40 = mm40
    entry.operator_name = operator_name
    entry.description = description
    db.commit()
    db.refresh(entry)
    return entry


def delete_dpr(entry_id: int, db: Session):
    entry = db.query(DPR).filter(DPR.id == entry_id).first()
    if not entry:
        raise HTTPException(404, "DPR entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "DPR entry deleted"}


def get_factory_dprs(db: Session, skip: int = 0, limit: int = 20,
                      month: Optional[int] = None, year: Optional[int] = None):
    q = db.query(FactoryDPR).order_by(FactoryDPR.date.desc())
    if month and year:
        q = q.filter(extract('month', FactoryDPR.date) == month, extract('year', FactoryDPR.date) == year)
    total = q.count()
    return total, q.offset(skip).limit(limit).all()


def create_factory_dpr(data: dict, uploaded_by: str, db: Session):
    entry = FactoryDPR(uploaded_by=uploaded_by, **data)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def update_factory_dpr(entry_id: int, data: dict, db: Session):
    entry = db.query(FactoryDPR).filter(FactoryDPR.id == entry_id).first()
    if not entry:
        raise HTTPException(404, "Factory DPR entry not found")
    for k, v in data.items():
        setattr(entry, k, v)
    db.commit()
    db.refresh(entry)
    return entry


def delete_factory_dpr(entry_id: int, db: Session):
    entry = db.query(FactoryDPR).filter(FactoryDPR.id == entry_id).first()
    if not entry:
        raise HTTPException(404, "Factory DPR entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Factory DPR entry deleted"}
