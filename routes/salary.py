from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.auth import get_current_employee
from middleware.rbac import require_hr_or_gm
from database.models import Employee as EmployeeDB
from models.salary import SalaryComputeRequest, SalaryDeductionResponse, BulkComputeRequest
from services.salary import compute_one, compute_all, save_deduction, get_deduction, get_my_deductions, get_all_deductions
from services.email import send_payslip_email
from services.whatsapp import send_payslip_whatsapp

router = APIRouter(prefix="/salary", tags=["salary"])


@router.get("/my")
def my_payslips(emp: EmployeeDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return get_my_deductions(emp.employee_id, db)


@router.post("/compute", dependencies=[Depends(require_hr_or_gm)])
def preview_one(req: SalaryComputeRequest, db: Session = Depends(get_db)):
    return compute_one(req.employee_id, req.month, req.year, req.advance_deduction, db)


@router.post("/compute/all", dependencies=[Depends(require_hr_or_gm)])
def preview_all(req: BulkComputeRequest, db: Session = Depends(get_db)):
    return compute_all(req.month, req.year, db)


@router.post("/save", response_model=SalaryDeductionResponse, dependencies=[Depends(require_hr_or_gm)])
def save_one(req: SalaryComputeRequest, bg: BackgroundTasks, db: Session = Depends(get_db)):
    rec, notif = save_deduction(req.employee_id, req.month, req.year, req.advance_deduction, db)
    if notif['email']:
        bg.add_task(send_payslip_email, notif['email'], notif['name'], notif['month_name'], notif['year'], notif['gross'], notif['deduction'], notif['net'])
    if notif['phone']:
        bg.add_task(send_payslip_whatsapp, notif['phone'], notif['name'], notif['month_name'], notif['year'], notif['net'])
    return rec


@router.get("/saved/{year}/{month}", dependencies=[Depends(require_hr_or_gm)])
def fetch_all_saved(year: int, month: int, db: Session = Depends(get_db)):
    return get_all_deductions(month, year, db)


@router.get("/{emp_id}/{year}/{month}", dependencies=[Depends(require_hr_or_gm)])
def fetch_one(emp_id: int, year: int, month: int, db: Session = Depends(get_db)):
    rec = get_deduction(emp_id, month, year, db)
    return rec or {}
