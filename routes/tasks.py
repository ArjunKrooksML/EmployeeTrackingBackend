from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.auth import get_current_employee
from database.models import Employee as EmpDB
from services import employee_tasks
from services.attachments import upload_att, get_atts, delete_att
from models.tasks import Task as TaskResponse
from typing import List

_UPLOAD_ROLES = {'hr', 'gm', 'senior'}

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/employee/{employee_id}", response_model=List[TaskResponse])
async def get_employee_tasks(employee_id: int, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    if employee_id != emp.employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot access another employee's tasks")
    return employee_tasks.get_employee_tasks(employee_id, db)


@router.get("/{task_id}/attachments")
async def list_attachments(task_id: int, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return get_atts(task_id, db)


@router.post("/{task_id}/attachments")
async def add_attachment(task_id: int, file: UploadFile = File(...), emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    if emp.role not in _UPLOAD_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return upload_att(task_id, file, db)


@router.delete("/{task_id}/attachments/{att_id}", status_code=204)
async def remove_attachment(task_id: int, att_id: int, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    if emp.role not in _UPLOAD_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    delete_att(att_id, task_id, db)


@router.put("/{task_id}/complete")
async def mark_task_complete(
    task_id: int,
    employee_id: int,
    is_completed: bool = True,
    emp: EmpDB = Depends(get_current_employee),
    db: Session = Depends(get_db)
):
    if employee_id != emp.employee_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another employee's task")
    return employee_tasks.update_task_status(task_id, employee_id, is_completed, db)
