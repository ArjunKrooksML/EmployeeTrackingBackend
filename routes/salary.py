from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from middleware.rbac import require_hr_or_gm
from models.salary import SalaryComputeRequest, SalaryDeductionResponse, BulkComputeRequest
from services.salary import compute_one, compute_all, save_deduction, get_deduction

router = APIRouter(prefix="/salary", tags=["salary"])


@router.post("/compute", dependencies=[Depends(require_hr_or_gm)])
def preview_one(req: SalaryComputeRequest, db: Session = Depends(get_db)):
    return compute_one(req.employee_id, req.month, req.year, req.advance_deduction, db)


@router.post("/compute/all", dependencies=[Depends(require_hr_or_gm)])
def preview_all(req: BulkComputeRequest, db: Session = Depends(get_db)):
    return compute_all(req.month, req.year, db)


@router.post("/save", response_model=SalaryDeductionResponse, dependencies=[Depends(require_hr_or_gm)])
def save_one(req: SalaryComputeRequest, db: Session = Depends(get_db)):
    return save_deduction(req.employee_id, req.month, req.year, req.advance_deduction, db)


@router.get("/{emp_id}/{year}/{month}", dependencies=[Depends(require_hr_or_gm)])
def fetch_one(emp_id: int, year: int, month: int, db: Session = Depends(get_db)):
    rec = get_deduction(emp_id, month, year, db)
    return rec or {}
