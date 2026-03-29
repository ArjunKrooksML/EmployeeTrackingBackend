from pydantic import BaseModel
from datetime import date, datetime, time
from typing import Optional


class AttBase(BaseModel):
    date: date
    attendance: str


class AttUpdate(BaseModel):
    attendance: str


class AttResp(BaseModel):
    id: int
    employee_id: int
    date: date
    attendance: str
    checkin: Optional[time]
    lat: Optional[float]
    lng: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class AttWithEmp(AttResp):
    employee_name: str
