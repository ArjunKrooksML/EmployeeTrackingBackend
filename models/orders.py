from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class POItemCreate(BaseModel):
    size: str
    quantity: int


class POCreate(BaseModel):
    po_number: str
    project_id: Optional[int] = None
    items: List[POItemCreate]


class POItemResponse(BaseModel):
    id: int
    size: str
    quantity: int

    class Config:
        from_attributes = True


class POResponse(BaseModel):
    id: int
    po_number: str
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    created_at: datetime
    items: List[POItemResponse]

    class Config:
        from_attributes = True


class SOItemCreate(BaseModel):
    size: str
    supplied_qty: int
    balance_qty: int


class SOCreate(BaseModel):
    po_id: int
    invoice_number: Optional[str] = None
    items: List[SOItemCreate]


class SOItemResponse(BaseModel):
    id: int
    size: str
    supplied_qty: int
    balance_qty: int

    class Config:
        from_attributes = True


class SOResponse(BaseModel):
    id: int
    po_id: int
    po_number: str
    invoice_number: Optional[str] = None
    project_name: Optional[str] = None
    created_at: datetime
    items: List[SOItemResponse]

    class Config:
        from_attributes = True


class POSizeSummary(BaseModel):
    size: str
    po_qty: int
    total_supplied: int
    balance: int
