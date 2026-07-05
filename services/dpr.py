from sqlalchemy.orm import Session
from database.models import DPR, Project
from fastapi import HTTPException
from datetime import date


def all_projects(db: Session):
    return db.query(Project).order_by(Project.name).all()


def get_dprs(project_id: int, db: Session, skip: int = 0, limit: int = 20):
    if not db.query(Project).filter(Project.project_id == project_id).first():
        raise HTTPException(404, "Project not found")
    q = db.query(DPR).filter(DPR.project_id == project_id).order_by(DPR.date.desc())
    total = q.count()
    return total, q.offset(skip).limit(limit).all()


def create_dpr(project_id: int, d: date, description: str, uploaded_by: str, db: Session):
    if not db.query(Project).filter(Project.project_id == project_id).first():
        raise HTTPException(404, "Project not found")
    entry = DPR(project_id=project_id, date=d, description=description, uploaded_by=uploaded_by)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
