from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services import employee_projects
from models.projects import ProjectCreate, ProjectUpdate, Project as ProjectResponse
from typing import List
from middleware.auth import get_current_employee

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/employee", response_model=List[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    """List all projects (employees can view all)"""
    projects = employee_projects.list_all_projects(db)
    return projects


@router.post("/employee/create", response_model=ProjectResponse)
async def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project (employees can create projects)"""
    project = employee_projects.create_project(project_data, db)
    return project


@router.put("/employee/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_employee = Depends(get_current_employee)
):
    """Update a project (protected - employees can edit projects)"""
    project = employee_projects.update_project(project_id, project_data, db)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
