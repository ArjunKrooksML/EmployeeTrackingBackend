from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.rbac import require_gm
from services.admin_tasks import list_tasks, create_task, update_task
from models.tasks import Task as TaskResp, TaskCreate, TaskUpdate

router = APIRouter(prefix="/admin/tasks", tags=["admin/tasks"])


@router.get("", response_model=List[TaskResp])
async def get_tasks(db: Session = Depends(get_db), _=Depends(require_gm)):
    return list_tasks(db)


@router.post("/create", response_model=TaskResp)
async def add_task(task: TaskCreate, db: Session = Depends(get_db), _=Depends(require_gm)):
    return create_task(task, db)


@router.put("/{task_id}", response_model=TaskResp)
async def edit_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db), _=Depends(require_gm)):
    updated = update_task(task_id, task, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated
