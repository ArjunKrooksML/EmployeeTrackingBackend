from pydantic import BaseModel
from typing import Optional


class ExpenseReview(BaseModel):
    status: str
    remarks: Optional[str] = None


class PaymentReq(BaseModel):
    amount: int
    remarks: Optional[str] = None


class MarkPaidReq(BaseModel):
    remarks: Optional[str] = None
