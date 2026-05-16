from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SalaryComputeRequest(BaseModel):
    employee_id: int
    month: int
    year: int
    advance_deduction: float = 0.0


class SalaryDeductionResponse(BaseModel):
    id: Optional[int] = None
    employee_id: int
    employee_name: Optional[str] = None
    month: int
    year: int
    basic: int
    da: int
    hra: int
    others: int
    gross_salary: int
    lates_count: int
    absents_from_lates: int
    half_day_absents: int
    full_absents: int
    paid_leave_used: bool
    leave_deduction: float
    advance_deduction: float
    total_deduction: float
    net_salary: float
    working_days: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BulkComputeRequest(BaseModel):
    month: int
    year: int
