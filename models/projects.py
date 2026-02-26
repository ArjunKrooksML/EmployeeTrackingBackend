from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class ProjectBase(BaseModel):
    name: str = Field(max_length=150)
    client_name: str = Field(max_length=150)
    address: str
    start_date: date
    completion_date: Optional[date] = None

    @model_validator(mode='after')
    def check_completion(cls, values):
        completion = values.completion_date
        start = values.start_date
        if completion and completion < start:
            raise ValueError('Completion date cannot be earlier than start date')
        return values


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    client_name: Optional[str] = Field(default=None, max_length=150)
    address: Optional[str] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None


class Project(ProjectBase):
    project_id: int

    class Config:
        from_attributes = True

