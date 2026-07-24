from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Literal


class ChaserCreate(BaseModel):
    date: date
    entry_type: Literal['issue', 'stock'] = 'issue'
    vendor: Optional[str] = None
    project_id: Optional[int] = None
    size_2_5: int = Field(0, ge=0)
    size_3: int = Field(0, ge=0)
    size_3_5: int = Field(0, ge=0)
    size_4: int = Field(0, ge=0)
    description: str = ''


class ChaserResp(BaseModel):
    id: int
    date: date
    entry_type: str
    vendor: Optional[str] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    size_2_5: int = 0
    size_3: int = 0
    size_3_5: int = 0
    size_4: int = 0
    description: str = ''
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockBalanceResp(BaseModel):
    size_2_5: int
    size_3: int
    size_3_5: int
    size_4: int
