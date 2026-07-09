from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DPRCreate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm32: int = 0
    operator_name: str = ''


class DPRUpdate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm32: int = 0
    operator_name: str = ''


class DPRResp(BaseModel):
    id: int
    project_id: int
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm32: int = 0
    operator_name: str = ''
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
