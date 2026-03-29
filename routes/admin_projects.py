from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.rbac import require_hr_or_gm
from services.admin_projects import list_projects, create_project, update_project
from models.projects import Project as ProjectResp, ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/admin/projects", tags=["admin/projects"])


@router.get("", response_model=List[ProjectResp])
async def get_projects(db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return list_projects(db)


@router.post("/create", response_model=ProjectResp)
async def add_project(project: ProjectCreate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return create_project(project, db)


@router.put("/{project_id}", response_model=ProjectResp)
async def edit_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    updated = update_project(project_id, project, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated