from pydantic import BaseModel
from datetime import date, datetime, time
from typing import Optional

class AttendanceBase(BaseModel):
    date: date
    attendance: str

class AttendanceUpdate(BaseModel):
    attendance: str

class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    date: date
    attendance: str
    checkin: Optional[time]
    created_at: datetime

    class Config:
        from_attributes = True

class AttendanceWithEmployee(AttendanceResponse):
    employee_name: str
