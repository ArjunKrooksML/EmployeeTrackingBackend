from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from database.models import Task as TaskDB
from models.tasks import TaskCreate, TaskUpdate


def list_tasks(db: Session) -> List[TaskDB]:
    return db.query(TaskDB).order_by(TaskDB.created.desc()).all()


def create_task(task_data: TaskCreate, db: Session) -> TaskDB:
    db_task = TaskDB(**task_data.model_dump())
    try:
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "tasks_project_id_fkey" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid project_id. Project does not exist.")
        raise HTTPException(status_code=400, detail="Unable to create task due to invalid data.")
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


def update_task(task_id: int, task_data: TaskUpdate, db: Session) -> Optional[TaskDB]:
    db_task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if not db_task:
        return None

    update_values = task_data.model_dump(exclude_unset=True)
    for field, value in update_values.items():
        setattr(db_task, field, value)

    try:
        db.commit()
        db.refresh(db_task)
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