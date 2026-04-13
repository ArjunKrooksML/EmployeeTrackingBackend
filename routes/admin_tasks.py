from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.rbac import require_gm
from services.admin_tasks import list_tasks, create_task, update_task
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
    _=Depends(require_gm),
):
    skip = (page - 1) * page_size
    return list_tasks(db, skip=skip, limit=page_size, page=page, page_size=page_size, status=status, priority=priority)


@router.post("/create", response_model=TaskResp)
async def add_task(task: TaskCreate, db: Session = Depends(get_db), _=Depends(require_gm)):
    return create_task(task, db)


@router.put("/{task_id}", response_model=TaskResp)
async def edit_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), _=Depends(require_gm)):
    updated = update_task(task_id, task, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated
