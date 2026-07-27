from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.auth import get_current_admin
from middleware.rbac import require_hr_or_gm
from models.expenses import ExpenseReview, PaymentReq, MarkPaidReq
from services import expenses as svc

router = APIRouter(prefix="/admin/expenses", tags=["admin-expenses"])


@router.get("")
def list_expenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_hr_or_gm),
):
    skip = (page - 1) * page_size
    total, items = svc.all_expenses(db, skip=skip, limit=page_size, status=status)
    pages = max(1, (total + page_size - 1) // page_size)
    return {"total": total, "page": page, "page_size": page_size, "pages": pages, "items": items}


@router.get("/{expense_id}")
def get_expense(expense_id: int, db: Session = Depends(get_db), _=Depends(require_hr_or_gm)):
    return svc.get_one(expense_id, db)


@router.put("/{expense_id}/review")
def review_expense(
    expense_id: int,
    data: ExpenseReview,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    return svc.review(expense_id, data.status, data.remarks, db)


@router.put("/{expense_id}/payment")
def record_payment(
    expense_id: int,
    data: PaymentReq,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    return svc.record_payment(expense_id, data.amount, data.remarks, db)


@router.put("/{expense_id}/paid")
def mark_paid(
    expense_id: int,
    data: Optional[MarkPaidReq] = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_admin),
):
    return svc.mark_paid(expense_id, data.remarks if data else None, db)
