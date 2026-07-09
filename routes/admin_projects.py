from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.rbac import require_hr_or_gm, require_hr_gm_or_senior
from services.admin_projects import list_projects, create_project, update_project, delete_project
from models.projects import Project as ProjectResp, ProjectCreate, ProjectUpdate
from models.pagination import PaginatedResponse

router = APIRouter(prefix="/admin/projects", tags=["admin/projects"])


@router.get("", response_model=PaginatedResponse[ProjectResp])
async def get_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    db: Session = Depends(get_db),
    _=Depends(require_hr_gm_or_senior),
):
    skip = (page - 1) * page_size
    return list_projects(db, skip=skip, limit=page_size, page=page, page_size=page_size)


@router.post("/create", response_model=ProjectResp)
async def add_project(project: ProjectCreate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return create_project(project, db)


@router.put("/{project_id}", response_model=ProjectResp)
async def edit_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    updated = update_project(project_id, project, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Project not found")
    return updated


@router.delete("/{project_id}", status_code=204)
async def remove_project(project_id: int, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    if not delete_project(project_id, db):
        raise HTTPException(status_code=404, detail="Project not found")
