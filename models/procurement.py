from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class VendorCreate(BaseModel):
    name: str


class VendorResp(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ProcurementItem(BaseModel):
    size: str
    qty_mt: float


class ProcurementCreate(BaseModel):
    date: date
    bill_no: str
    vendor_id: int
    heat_no: Optional[str] = None
    tc_no: Optional[str] = None
    lot_no: Optional[str] = None
    test_report_no: Optional[str] = None
    items: List[ProcurementItem]


class ProcurementResp(BaseModel):
    id: int
    date: date
    bill_no: str
    vendor_id: Optional[int] = None
    vendor_name: Optional[str] = None
    heat_no: Optional[str] = None
    tc_no: Optional[str] = None
    lot_no: Optional[str] = None
    test_report_no: Optional[str] = None
    items: List[ProcurementItem]
    uploaded_by: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
