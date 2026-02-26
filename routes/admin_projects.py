from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.admin_projects import list_projects, create_project, update_project
from models.projects import Project as ProjectResponse, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/admin/projects", tags=["admin/projects"])


@router.get("", response_model=List[ProjectResponse])
async def get_all_projects_route(db: Session = Depends(get_db)):
    return list_projects(db)


@router.post("/create", response_model=ProjectResponse)
async def create_project_route(project: ProjectCreate, db: Session = Depends(get_db)):
    return create_project(project, db)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project_route(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    updated = update_project(project_id, project, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated