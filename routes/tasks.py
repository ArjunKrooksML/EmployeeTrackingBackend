from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services import employee_tasks
from models.tasks import Task as TaskResponse
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/employee/{employee_id}", response_model=List[TaskResponse])
async def get_employee_tasks(employee_id: int, db: Session = Depends(get_db)):
    return employee_tasks.get_employee_tasks(employee_id, db)


@router.put("/{task_id}/complete")
async def mark_task_complete(
    task_id: int,
    employee_id: int,
    is_completed: bool = True,
    db: Session = Depends(get_db)
):
    return employee_tasks.update_task_status(task_id, employee_id, is_completed, db)
