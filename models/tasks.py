from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    project_id: int
    task_name: str = Field(max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    iscompleted: Optional[bool] = False
    status: str = Field(max_length=100)
    priority: str = Field(max_length=100)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    project_id: Optional[int] = None
    task_name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    start_date: Optional[date] = None
    deadline: Optional[date] = None
    iscompleted: Optional[bool] = None
    status: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[str] = Field(default=None, max_length=100)


class Task(TaskBase):
    task_id: int
    created: datetime

    class Config:
        from_attributes = True

