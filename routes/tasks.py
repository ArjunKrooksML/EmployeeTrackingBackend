from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from services import employee_tasks
from models.tasks import Task as TaskResponse
from typing import List

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/employee/{employee_name}", response_model=List[TaskResponse])
async def get_employee_tasks(employee_name: str, db: Session = Depends(get_db)):
    """Get all tasks assigned to an employee"""
    tasks = employee_tasks.get_employee_tasks(employee_name, db)
    return tasks


@router.put("/{task_id}/complete")
async def mark_task_complete(
    task_id: int,
    employee_name: str,
    is_completed: bool = True,
    db: Session = Depends(get_db)
):
    """Mark a task as completed (only if assigned to employee)"""
    task = employee_tasks.update_task_status(task_id, employee_name, is_completed, db)
    return task
