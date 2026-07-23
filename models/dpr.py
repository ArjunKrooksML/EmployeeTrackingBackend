from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class DPRCreate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm28: int = 0
    mm32: int = 0
    mm40: int = 0
    operator_name: str = ''
    description: str = ''


class DPRUpdate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm28: int = 0
    mm32: int = 0
    mm40: int = 0
    operator_name: str = ''
    description: str = ''


class DPRResp(BaseModel):
    id: int
    project_id: int
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm28: int = 0
    mm32: int = 0
    mm40: int = 0
    operator_name: str = ''
    description: str = ''
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FactoryDPRCreate(BaseModel):
    date: date
    mm16: int = 0
    mm20: int = 0
    mm25: int = 0
    mm28: int = 0
    mm32: int = 0
    mm40: int = 0
    r20_16: int = 0
    r25_16: int = 0
    r25_20: int = 0
    r32_20: int = 0
    r32_16: int = 0
    r32_25: int = 0
    r40_25: int = 0
    r40_32: int = 0
    description: str = ''


class FactoryDPRUpdate(FactoryDPRCreate):
    pass


class FactoryDPRResp(FactoryDPRCreate):
    id: int
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
