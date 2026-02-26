from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
from middleware.helpers import validate_email, validate_password


class AdminBase(BaseModel):
    email: EmailStr
    role: str = "admin"
    permissions: List[str] = ["user_management"]
    is_active: bool = True

    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v


class AdminCreate(AdminBase):
    password: str = Field(min_length=6, max_length=100)

    @field_validator('password')
    @classmethod
    def check_password(cls, v: str) -> str:
        if not validate_password(v):
            raise ValueError('Password must be between 6 and 100 characters')
        return v


class AdminLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v


class Admin(AdminBase):
    admin_id: int
    password: str
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        from_attributes = True


class AdminPasswordReset(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str = Field(min_length=8, max_length=100)

    @field_validator('email')
    @classmethod
    def check_email(cls, v: str) -> str:
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('old_password')
    @classmethod
    def check_old_password(cls, v: str) -> str:
        if not validate_password(v):
            raise ValueError('Invalid old password format')
        return v

    @field_validator('new_password')
    @classmethod
    def check_password(cls, v: str) -> str:
        if not validate_password(v, min_length=8):
            raise ValueError('Password must be at least 8 characters')
        return v


class AdminPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
