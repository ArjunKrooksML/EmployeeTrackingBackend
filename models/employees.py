from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date
from middleware.helpers import validate_phone, validate_date, validate_id_number, validate_email, validate_password


class EmployeeBase(BaseModel):
    employee_name: str = Field(max_length=150)
    email: str = Field(max_length=255)
    password: Optional[str] = None
    dob: date
    address: str
    phone_no: str = Field(max_length=15)
    id_type: str
    id_number: str = Field(max_length=50)
    year_joined: Optional[str] = Field(max_length=10, default=None)
    basic: int = 0
    da: int = 0
    hra: int = 0
    others: int = 0
    role: Optional[str] = 'employee'

    @field_validator('password')
    @classmethod
    def check_password(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_password(v):
            raise ValueError('Password must be between 6 and 100 characters')
        return v

    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('phone_no')
    @classmethod
    def check_phone(cls, v: str) -> str:
        if not validate_phone(v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('dob', mode='before')
    @classmethod
    def check_dob(cls, v) -> date:
        if isinstance(v, str):
            if not validate_date(v):
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

    @model_validator(mode='after')
    def check_id_number_with_type(self):
        if not validate_id_number(self.id_number, self.id_type):
            id_type_lower = self.id_type.lower() if self.id_type else ''
            if id_type_lower in ['aadhaar', 'aadhar']:
                raise ValueError('Aadhaar number must be exactly 12 digits')
            elif id_type_lower == 'pan':
                raise ValueError('PAN must be exactly 10 alphanumeric characters')
            elif id_type_lower == 'passport':
                raise ValueError('Passport must be exactly 8 alphanumeric characters')
            raise ValueError('Invalid ID number')
        return self


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeImport(BaseModel):
    employee_name: str = Field(max_length=150)
    email: str = Field(max_length=255)
    password: Optional[str] = None
    dob: Optional[date] = None
    address: str
    phone_no: str = Field(max_length=15)
    id_type: str
    id_number: str = Field(max_length=50)
    year_joined: Optional[str] = Field(max_length=10, default=None)
    basic: int = 0
    da: int = 0
    hra: int = 0
    others: int = 0

    @field_validator('password')
    @classmethod
    def check_password(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_password(v):
            raise ValueError('Password must be between 6 and 100 characters')
        return v

    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('phone_no')
    @classmethod
    def check_phone(cls, v: str) -> str:
        if not validate_phone(v):
            raise ValueError('Invalid phone number format')
        return v

    @field_validator('dob', mode='before')
    @classmethod
    def check_dob(cls, v) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, str):
            if not validate_date(v):
                raise ValueError('Invalid date format. Use YYYY-MM-DD')
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

    @model_validator(mode='after')
    def check_id_number_with_type(self):
        if not validate_id_number(self.id_number, self.id_type):
            id_type_lower = self.id_type.lower() if self.id_type else ''
            if id_type_lower in ['aadhaar', 'aadhar']:
                raise ValueError('Aadhaar number must be exactly 12 digits')
            elif id_type_lower == 'pan':
                raise ValueError('PAN must be exactly 10 alphanumeric characters')
            elif id_type_lower == 'passport':
                raise ValueError('Passport must be exactly 8 alphanumeric characters')
            raise ValueError('Invalid ID number')
        return self


class EmployeeUpdate(BaseModel):
    employee_name: Optional[str] = Field(max_length=150, default=None)
    email: Optional[str] = Field(max_length=255, default=None)
    password: Optional[str] = None
    dob: Optional[date] = None
    address: Optional[str] = None
    phone_no: Optional[str] = Field(max_length=15, default=None)
    id_type: Optional[str] = None
    id_number: Optional[str] = Field(max_length=50, default=None)
    year_joined: Optional[str] = Field(max_length=10, default=None)
    basic: Optional[int] = None
    da: Optional[int] = None
    hra: Optional[int] = None
    others: Optional[int] = None
    role: Optional[str] = None

    @field_validator('password')
    @classmethod
    def check_password(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_password(v):
            raise ValueError('Password must be between 6 and 100 characters')
        return v

    @field_validator('email')
    @classmethod
    def check_email(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_email(v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('phone_no')
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not validate_phone(v):
            raise ValueError('Invalid phone number format')
        return v

    @model_validator(mode='after')
    def check_id_number_with_type(self):
        if self.id_number and self.id_type:
            if not validate_id_number(self.id_number, self.id_type):
                id_type_lower = self.id_type.lower()
                if id_type_lower in ['aadhaar', 'aadhar']:
                    raise ValueError('Aadhaar number must be exactly 12 digits')
                elif id_type_lower == 'pan':
                    raise ValueError('PAN must be exactly 10 alphanumeric characters')
                elif id_type_lower == 'passport':
                    raise ValueError('Passport must be exactly 8 alphanumeric characters')
                raise ValueError('Invalid ID number')
        return self


class Employee(EmployeeBase):
    employee_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeResponse(BaseModel):
    employee_id: int
    employee_name: str
    email: str
    dob: date
    address: str
    phone_no: str
    id_type: str
    id_number: str
    year_joined: Optional[str] = None
    basic: int = 0
    da: int = 0
    hra: int = 0
    others: int = 0
    role: str = 'employee'
    created_at: datetime
    updated_at: datetime
    generated_password: Optional[str] = None
    profile_pic_url: Optional[str] = None

    class Config:
        from_attributes = True


class EmployeeLogin(BaseModel):
    email: str
    password: str


class EmployeePublic(BaseModel):
    employee_id: int
    employee_name: str
    email: str
    dob: date
    address: str
    phone_no: str
    id_type: str
    id_number: str
    year_joined: Optional[str] = None
    basic: int = 0
    da: int = 0
    hra: int = 0
    others: int = 0
    role: str = 'employee'
    profile_pic_url: Optional[str] = None

    class Config:
        from_attributes = True
