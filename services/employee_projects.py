from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import Project as ProjectDB
from models.projects import ProjectCreate, ProjectUpdate


def list_all_projects(db: Session) -> List[ProjectDB]:
    """List all projects (employees can view all projects)"""
    try:
        return db.query(ProjectDB).order_by(ProjectDB.project_id.desc()).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")


def create_project(project_data: ProjectCreate, db: Session) -> ProjectDB:
    """Create a new project (employees can create projects)"""
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
    """Update a project (employees can edit projects)"""
    project = db.query(ProjectDB).filter(ProjectDB.project_id == project_id).first()
    if not project:
        return None
    
    update_data = project_data.model_dump(exclude_unset=True)
    
    if 'completion_date' in update_data and 'start_date' in update_data:
        if update_data['completion_date'] and update_data['completion_date'] < update_data['start_date']:
            raise HTTPException(status_code=400, detail='Completion date cannot be earlier than start date')
    elif 'completion_date' in update_data and update_data['completion_date']:
        if update_data['completion_date'] < project.start_date:
            raise HTTPException(status_code=400, detail='Completion date cannot be earlier than start date')
    elif 'start_date' in update_data:
        if project.completion_date and project.completion_date < update_data['start_date']:
            raise HTTPException(status_code=400, detail='Completion date cannot be earlier than start date')
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    try:
        db.commit()
        db.refresh(project)
        return project
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

