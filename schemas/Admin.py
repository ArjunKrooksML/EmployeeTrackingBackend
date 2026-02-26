from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime, date
from middleware.helpers import validate_email, validate_password

class AddEmployee(BaseModel):
    employee_name: str = Field(max_length=150)
    dob: date
    address: str
    phone_no: str = Field(max_length=15)
    id_type: str
    id_number: str = Field(max_length=50)
    designation_id: Optional[int] = None
    year_joined: Optional[str] = Field(max_length=10, default=None)
    salary: int
