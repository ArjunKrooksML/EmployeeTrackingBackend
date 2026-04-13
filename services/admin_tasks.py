from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database.models import Task as TaskDB, Employee as EmpDB
from models.tasks import TaskCreate, TaskUpdate
from services.email import send_task_assigned_email


def list_tasks(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
) -> dict:
    """Admin function: List all tasks with optional filters"""
    q = db.query(TaskDB)
    if status:
        q = q.filter(TaskDB.status == status)
    if priority:
        q = q.filter(TaskDB.priority == priority)
    total = q.count()
    items = q.order_by(TaskDB.created.desc()).offset(skip).limit(limit).all()
    pages = (total + page_size - 1) // page_size if page_size else 1
    return {"items": items, "total": total, "page": page, "page_size": page_size, "pages": pages}


def _notify_assigned(employee_id: int, task: TaskDB, db: Session):
    emp = db.query(EmpDB).filter(EmpDB.employee_id == employee_id).first()
    if emp:
        try:
            send_task_assigned_email(emp.email, emp.employee_name, task.task_name, task.description, str(task.deadline) if task.deadline else None)
        except Exception as e:
            print(f"[email] Failed to send task assignment email: {e}")


def create_task(task_data: TaskCreate, db: Session) -> TaskDB:
    db_task = TaskDB(**task_data.model_dump())
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        if db_task.assigned_to:
            _notify_assigned(db_task.assigned_to, db_task, db)
        return db_task
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "tasks_project_id_fkey" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid project_id. Project does not exist.")
        if "tasks_assigned_to_fkey" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid assigned_to. Employee does not exist.")
        raise HTTPException(status_code=400, detail="Unable to create task due to invalid data.")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


def update_task(task_id: int, task_data: TaskUpdate, db: Session) -> Optional[TaskDB]:
    db_task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if not db_task:
        return None

    update_values = task_data.model_dump(exclude_unset=True)
    prev_assigned = db_task.assigned_to
    for field, value in update_values.items():
        setattr(db_task, field, value)

    try:
        db.commit()
        db.refresh(db_task)
        if db_task.assigned_to and db_task.assigned_to != prev_assigned:
            _notify_assigned(db_task.assigned_to, db_task, db)
        return db_task
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "tasks_project_id_fkey" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid project_id. Project does not exist.")
        raise HTTPException(status_code=400, detail="Unable to update task due to invalid data.")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")