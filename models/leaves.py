from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime

class LeaveCreate(BaseModel):
    employee_id: Optional[int] = None
    leave_type: str
    leave_date: date
    day_type: str
    reason: Optional[str] = None

class LeaveUpdateStatus(BaseModel):
    status: str  # 'approved', 'rejected'

class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    leave_type: str
    leave_date: date
    day_type: str
    status: str
    reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AdminLeaveResponse(LeaveResponse):
    employee_name: str
    profile_pic_url: Optional[str] = None
