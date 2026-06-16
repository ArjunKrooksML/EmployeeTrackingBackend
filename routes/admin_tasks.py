from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.rbac import require_gm_or_senior
from services.admin_tasks import list_tasks, create_task, update_task, delete_task
from services.attachments import upload_att, get_atts, delete_att
from models.tasks import Task as TaskResp, TaskCreate, TaskUpdate
from models.pagination import PaginatedResponse

router = APIRouter(prefix="/admin/tasks", tags=["admin/tasks"])


@router.get("", response_model=PaginatedResponse[TaskResp])
async def get_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=10000),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_gm_or_senior),
):
    skip = (page - 1) * page_size
    return list_tasks(db, skip=skip, limit=page_size, page=page, page_size=page_size, status=status, priority=priority)


@router.post("/create", response_model=TaskResp)
async def add_task(task: TaskCreate, db: Session = Depends(get_db), _=Depends(require_gm_or_senior)):
    return create_task(task, db)


@router.put("/{task_id}", response_model=TaskResp)
async def edit_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), _=Depends(require_gm_or_senior)):
    updated = update_task(task_id, task, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=204)
async def remove_task(task_id: int, db: Session = Depends(get_db), _=Depends(require_gm_or_senior)):
    if not delete_task(task_id, db):
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/attachments")
async def add_attachment(task_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), _=Depends(require_gm_or_senior)):
    return upload_att(task_id, file, db)


@router.get("/{task_id}/attachments")
async def list_attachments(task_id: int, db: Session = Depends(get_db), _=Depends(require_gm_or_senior)):
    return get_atts(task_id, db)


@router.delete("/{task_id}/attachments/{att_id}", status_code=204)
async def remove_attachment(task_id: int, att_id: int, db: Session = Depends(get_db), _=Depends(require_gm_or_senior)):
    delete_att(att_id, task_id, db)
