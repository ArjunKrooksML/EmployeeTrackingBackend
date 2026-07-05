from pydantic import BaseModel
from typing import Optional


class ExpenseReview(BaseModel):
    status: str
    remarks: Optional[str] = None
