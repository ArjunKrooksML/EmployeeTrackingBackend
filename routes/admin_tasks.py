from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services.admin_tasks import list_tasks, create_task, update_task
from models.tasks import Task as TaskResponse, TaskCreate, TaskUpdate

router = APIRouter(prefix="/admin/tasks", tags=["admin/tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_all_tasks_route(db: Session = Depends(get_db)):
    return list_tasks(db)


@router.post("/create", response_model=TaskResponse)
async def create_task_route(task: TaskCreate, db: Session = Depends(get_db)):
    return create_task(task, db)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task_route(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    updated = update_task(task_id, task, db)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

