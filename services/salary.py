import calendar
from datetime import date
from typing import List, Optional, Tuple
from fastapi import HTTPException
from sqlalchemy.orm import Session
from database.models import Employee as EmpDB, Attendance as AttDB, SalaryDeduction as SalaryDB


def _calc(emp: EmpDB, month: int, year: int, advance_deduction: float, att_records: list) -> dict:
    lates = sum(1 for a in att_records if a.attendance == 'late')
    half_day_absents = sum(1 for a in att_records if a.attendance == 'absent' and a.checkin is not None)
    full_absents = sum(1 for a in att_records if a.attendance == 'absent' and a.checkin is None)

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
        "net_salary": round(gross - total_deduction, 2),
        "working_days": working_days,
    }


def _compute(emp: EmpDB, month: int, year: int, advance_deduction: float, db: Session) -> dict:
    from_date = date(year, month, 1)
    to_date = date(year, month, calendar.monthrange(year, month)[1])
    att = db.query(AttDB).filter(
        AttDB.employee_id == emp.employee_id,
        AttDB.date >= from_date,
        AttDB.date <= to_date
    ).all()
    return _calc(emp, month, year, advance_deduction, att)


def compute_one(emp_id: int, month: int, year: int, advance_deduction: float, db: Session) -> dict:
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _compute(emp, month, year, advance_deduction, db)


def compute_all(month: int, year: int, db: Session) -> List[dict]:
    from_date = date(year, month, 1)
    to_date = date(year, month, calendar.monthrange(year, month)[1])

    emps = db.query(EmpDB).all()
    if not emps:
        return []
    emp_ids = [e.employee_id for e in emps]

    advances = {
        s.employee_id: s.advance_deduction
        for s in db.query(SalaryDB).filter(
            SalaryDB.employee_id.in_(emp_ids),
            SalaryDB.month == month,
            SalaryDB.year == year
        ).all()
    }

    att_by_emp: dict = {}
    for a in db.query(AttDB).filter(
        AttDB.employee_id.in_(emp_ids),
        AttDB.date >= from_date,
        AttDB.date <= to_date
    ).all():
        att_by_emp.setdefault(a.employee_id, []).append(a)

    return [
        _calc(
            emp, month, year,
            advances.get(emp.employee_id, 0.0),
            att_by_emp.get(emp.employee_id, []),
        )
        for emp in emps
    ]


def save_deduction(emp_id: int, month: int, year: int, advance_deduction: float, db: Session) -> Tuple:
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
            if k != 'employee_name' and hasattr(rec, k):
                setattr(rec, k, v)
    else:
        rec = SalaryDB(**{k: v for k, v in data.items() if k != 'employee_name'})
        db.add(rec)

    try:
        db.commit()
        db.refresh(rec)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    notif = {
        'email': emp.email,
        'phone': emp.phone_no,
        'name': emp.employee_name,
        'month_name': calendar.month_name[month],
        'year': year,
        'gross': data['gross_salary'],
        'deduction': data['total_deduction'],
        'net': data['net_salary'],
    }
    return rec, notif


def get_deduction(emp_id: int, month: int, year: int, db: Session) -> Optional[SalaryDB]:
    return db.query(SalaryDB).filter(
        SalaryDB.employee_id == emp_id,
        SalaryDB.month == month,
        SalaryDB.year == year
    ).first()


def get_all_deductions(month: int, year: int, db: Session) -> List[dict]:
    rows = db.query(SalaryDB, EmpDB.employee_name).join(
        EmpDB, SalaryDB.employee_id == EmpDB.employee_id
    ).filter(SalaryDB.month == month, SalaryDB.year == year).all()
    out = []
    for rec, name in rows:
        d = {c.name: getattr(rec, c.name) for c in rec.__table__.columns}
        d['employee_name'] = name
        out.append(d)
    return out


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
