from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DPRCreate(BaseModel):
    date: date
    description: str


class DPRResp(BaseModel):
    id: int
    project_id: int
    date: date
    description: str
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
