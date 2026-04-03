from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import Task as TaskDB
from database.models import Project as ProjectDB


def get_employee_tasks(employee_name: str, db: Session) -> List[TaskDB]:
    """Get all tasks assigned to a specific employee"""
    try:
        tasks = db.query(TaskDB).filter(TaskDB.assigned_to == employee_name).order_by(TaskDB.created_at.desc()).all()
        return tasks
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


def update_task_status(task_id: int, employee_name: str, is_completed: bool, db: Session) -> TaskDB:
    """Update task completion status (only if assigned to employee)"""
    task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assigned_to != employee_name:
        raise HTTPException(status_code=403, detail="You are not assigned to this task")
    
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


def get_task_with_project(task_id: int, employee_name: str, db: Session) -> dict:
    """Get task details with project information"""
    task = db.query(TaskDB).filter(TaskDB.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.assigned_to != employee_name:
        raise HTTPException(status_code=403, detail="You are not assigned to this task")
    
    project = db.query(ProjectDB).filter(ProjectDB.project_id == task.project_id).first()
    
    return {
        "task": task,
        "project": project
    }

