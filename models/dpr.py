from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DPRCreate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm32: int = 0
    forging_qty: int = 0


class DPRUpdate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm32: int = 0
    forging_qty: int = 0


class DPRResp(BaseModel):
    id: int
    project_id: int
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm32: int = 0
    forging_qty: int = 0
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
