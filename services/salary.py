import calendar
from datetime import date
from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Employee as EmpDB, Attendance as AttDB, Leave as LeaveDB, SalaryDeduction as SalaryDB


def _compute(emp: EmpDB, month: int, year: int, advance_deduction: float, db: Session) -> dict:
    from_date = date(year, month, 1)
    to_date = date(year, month, calendar.monthrange(year, month)[1])

    att_records = db.query(AttDB).filter(
        AttDB.employee_id == emp.employee_id,
        AttDB.date >= from_date,
        AttDB.date <= to_date
    ).all()

    # Emergency leave dates — these are exempt from deductions
    emergency_dates = {
        str(l.leave_date) for l in db.query(LeaveDB).filter(
            LeaveDB.employee_id == emp.employee_id,
            LeaveDB.leave_date >= from_date,
            LeaveDB.leave_date <= to_date,
            LeaveDB.status == 'approved',
            LeaveDB.leave_type == 'emergency'
        ).all()
    }

    lates = sum(1 for a in att_records if a.attendance == 'late')
    # absent with check-in = half-day (checked in at/after 2pm)
    half_day_absents = sum(1 for a in att_records if a.attendance == 'absent' and a.checkin is not None)
    # absent without check-in = full absent, excluding emergency leave dates
    full_absents = sum(
        1 for a in att_records
        if a.attendance == 'absent' and a.checkin is None and str(a.date) not in emergency_dates
    )

    absents_from_lates = lates // 3
    total_deductible = full_absents + (half_day_absents * 0.5) + absents_from_lates

    paid_leave_used = total_deductible >= 1
    if paid_leave_used:
        total_deductible -= 1

    gross = emp.basic + emp.da + emp.hra + emp.others
    working_days = calendar.monthrange(year, month)[1]
    daily_rate = gross / working_days if working_days else 0

    leave_deduction = round(total_deductible * daily_rate, 2)
    total_deduction = round(leave_deduction + advance_deduction, 2)
    net_salary = round(gross - total_deduction, 2)

    return {
        "employee_id": emp.employee_id,
        "employee_name": emp.employee_name,
        "month": month,
        "year": year,
        "basic": emp.basic,
        "da": emp.da,
        "hra": emp.hra,
        "others": emp.others,
        "gross_salary": gross,
        "lates_count": lates,
        "absents_from_lates": absents_from_lates,
        "half_day_absents": half_day_absents,
        "full_absents": full_absents,
        "paid_leave_used": paid_leave_used,
        "leave_deduction": leave_deduction,
        "advance_deduction": advance_deduction,
        "total_deduction": total_deduction,
        "net_salary": net_salary,
        "working_days": working_days,
    }


def compute_one(emp_id: int, month: int, year: int, advance_deduction: float, db: Session) -> dict:
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _compute(emp, month, year, advance_deduction, db)


def compute_all(month: int, year: int, db: Session) -> List[dict]:
    emps = db.query(EmpDB).all()
    results = []
    for emp in emps:
        # Use saved advance_deduction if a record already exists, else 0
        saved = db.query(SalaryDB).filter(
            SalaryDB.employee_id == emp.employee_id,
            SalaryDB.month == month,
            SalaryDB.year == year
        ).first()
        adv = saved.advance_deduction if saved else 0.0
        results.append(_compute(emp, month, year, adv, db))
    return results


def save_deduction(emp_id: int, month: int, year: int, advance_deduction: float, db: Session) -> SalaryDB:
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    data = _compute(emp, month, year, advance_deduction, db)
    rec = db.query(SalaryDB).filter(
        SalaryDB.employee_id == emp_id,
        SalaryDB.month == month,
        SalaryDB.year == year
    ).first()

    if rec:
        for k, v in data.items():
            if k not in ('employee_name',) and hasattr(rec, k):
                setattr(rec, k, v)
    else:
        rec = SalaryDB(**{k: v for k, v in data.items() if k != 'employee_name'})
        db.add(rec)

    try:
        db.commit()
        db.refresh(rec)
        return rec
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_deduction(emp_id: int, month: int, year: int, db: Session) -> Optional[SalaryDB]:
    return db.query(SalaryDB).filter(
        SalaryDB.employee_id == emp_id,
        SalaryDB.month == month,
        SalaryDB.year == year
    ).first()


def get_my_deductions(emp_id: int, db: Session) -> List[dict]:
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        return []
    recs = db.query(SalaryDB).filter(
        SalaryDB.employee_id == emp_id
    ).order_by(SalaryDB.year.desc(), SalaryDB.month.desc()).all()
    out = []
    for rec in recs:
        d = {c.name: getattr(rec, c.name) for c in rec.__table__.columns}
        d['employee_name'] = emp.employee_name
        out.append(d)
    return out
