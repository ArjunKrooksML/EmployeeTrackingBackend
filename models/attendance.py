from pydantic import BaseModel, field_validator
from datetime import date, datetime, time
from typing import Optional


class CheckinReq(BaseModel):
    employee_id: int
    lat: Optional[float] = None
    lng: Optional[float] = None


class AttBase(BaseModel):
    date: date
    attendance: str


class AttUpdate(BaseModel):
    attendance: str

    @field_validator('attendance')
    @classmethod
    def check_status(cls, v: str) -> str:
        if v not in ['present', 'absent', 'late']:
            raise ValueError('Status must be present, absent, or late')
        return v


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
