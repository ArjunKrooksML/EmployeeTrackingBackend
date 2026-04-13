from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import Task as TaskDB
from database.models import Project as ProjectDB


def get_employee_tasks(employee_id: int, db: Session) -> List[TaskDB]:
    try:
        return db.query(TaskDB).filter(TaskDB.assigned_to == employee_id).order_by(TaskDB.created.desc()).all()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


def update_task_status(task_id: int, employee_id: int, is_completed: bool, db: Session) -> TaskDB:
    task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.assigned_to != employee_id:
        raise HTTPException(status_code=403, detail="Task not assigned to you")
    task.iscompleted = is_completed
    if is_completed:
        task.status = 'completed'
    try:
        db.commit()
        db.refresh(task)
        return task
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


def get_task_with_project(task_id: int, employee_id: int, db: Session) -> dict:
    task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.assigned_to != employee_id:
        raise HTTPException(status_code=403, detail="You are not assigned to this task")
    project = db.query(ProjectDB).filter(ProjectDB.project_id == task.project_id).first()
    return {"task": task, "project": project}
