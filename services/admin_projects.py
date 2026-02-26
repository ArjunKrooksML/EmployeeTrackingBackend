from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from database.models import Project as ProjectDB
from models.projects import ProjectCreate, ProjectUpdate


def list_projects(db: Session) -> List[ProjectDB]:
    return db.query(ProjectDB).order_by(ProjectDB.project_id.desc()).all()


def create_project(project_data: ProjectCreate, db: Session) -> ProjectDB:
    if project_data.completion_date and project_data.completion_date < project_data.start_date:
        raise HTTPException(status_code=400, detail='Completion date cannot be earlier than start date')

    db_project = ProjectDB(**project_data.model_dump())
    try:
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")


def update_project(project_id: int, project_data: ProjectUpdate, db: Session) -> Optional[ProjectDB]:
    db_project = db.query(ProjectDB).filter(ProjectDB.project_id == project_id).first()
    if not db_project:
        return None

    update_values = project_data.model_dump(exclude_unset=True)
    start = update_values.get('start_date', db_project.start_date)
    completion = update_values.get('completion_date', db_project.completion_date)

    if completion and completion < start:
        raise HTTPException(status_code=400, detail='Completion date cannot be earlier than start date')

    for field, value in update_values.items():
        setattr(db_project, field, value)

    try:
        db.commit()
        db.refresh(db_project)
        return db_project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

