from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import date
from fastapi import HTTPException
from models.employees import EmployeeCreate, EmployeeUpdate, EmployeeImport
from database.models import Employee as EmployeeDB
from middleware.helpers import hash_pwd, val_desig_id
import secrets


def norm_id_type(id_type: str) -> str:
    id_lower = id_type.strip().lower()
    mapping = {'aadhaar': 'aadhar', 'aadhar': 'aadhar', 'pan': 'pan', 'passport': 'passport'}
    return mapping.get(id_lower, 'aadhar')


def _get_enum_val(db: Session, norm_type: str) -> str:
    try:
        result = db.execute(text("SELECT udt_name FROM information_schema.columns WHERE table_name = 'employees' AND column_name = 'id_type'"))
        row = result.first()
        if row:
            enum_name = row[0]
            enum_res = db.execute(text(f"SELECT enumlabel FROM pg_enum WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = '{enum_name}') ORDER BY enumsortorder"))
            enum_vals = [r[0] for r in enum_res]
            if enum_vals:
                for ev in enum_vals:
                    if ev.lower() == norm_type.lower():
                        return ev
    except Exception:
        pass
    return norm_type


def _handle_db_err(e: Exception, desig_id: Optional[int] = None) -> None:
    err_msg = str(e).lower()
    if "foreign key constraint" in err_msg and "designation_id" in err_msg:
        raise HTTPException(status_code=400, detail=f"Designation ID {desig_id} does not exist")
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


def add_emp(data: EmployeeCreate, db: Session) -> EmployeeDB:
    val_desig_id(data.designation_id, db)
    id_type = _get_enum_val(db, norm_id_type(data.id_type))
    # Generate random password if one wasn't provided
    pwd = data.password or _gen_def_pwd(data.email)
    emp = EmployeeDB(
        employee_name=data.employee_name,
        email=data.email,
        password=hash_pwd(pwd),
        dob=data.dob,
        address=data.address,
        phone_no=data.phone_no,
        id_type=id_type,
        id_number=data.id_number,
        designation_id=data.designation_id,
        year_joined=data.year_joined,
        salary=data.salary,
    )
    try:
        db.add(emp)
        db.commit()
        db.refresh(emp)
        return emp
    except Exception as e:
        db.rollback()
        _handle_db_err(e, data.designation_id)


def get_all(db: Session) -> List[EmployeeDB]:
    return db.query(EmployeeDB).order_by(EmployeeDB.created_at.desc()).all()


def get_by_id(emp_id: int, db: Session) -> Optional[EmployeeDB]:
    return db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()


def update_emp(emp_id: int, data: EmployeeUpdate, db: Session) -> Optional[EmployeeDB]:
    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()
    if not emp:
        return None
    upd = data.model_dump(exclude_unset=True)
    if 'designation_id' in upd:
        val_desig_id(upd['designation_id'], db)
    if 'id_type' in upd:
        upd['id_type'] = _get_enum_val(db, norm_id_type(upd['id_type']))
    if 'password' in upd:
        upd['password'] = hash_pwd(upd['password'])
    for k, v in upd.items():
        setattr(emp, k, v)
    try:
        db.commit()
        db.refresh(emp)
        return emp
    except Exception as e:
        db.rollback()
        _handle_db_err(e, upd.get('designation_id'))


def delete_emp(emp_id: int, db: Session) -> bool:
    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()
    if not emp:
        return False
    db.delete(emp)
    db.commit()
    return True


def _gen_def_pwd(email: str) -> str:
    prefix = email.split('@')[0] if '@' in email else 'emp'
    return f"{prefix}@{secrets.token_hex(4)}"


def import_emps(data: List[EmployeeImport], db: Session) -> List[EmployeeDB]:
    emps = []
    errs = []
    for idx, d in enumerate(data, start=1):
        try:
            val_desig_id(d.designation_id, db)
        except HTTPException as e:
            errs.append(f"Row {idx}: {e.detail}")
            continue
        pwd = d.password or _gen_def_pwd(d.email)
        dob_val = d.dob or date(1990, 1, 1)
        emp = EmployeeDB(
            employee_name=d.employee_name,
            email=d.email,
            password=hash_pwd(pwd),
            dob=dob_val,
            address=d.address,
            phone_no=d.phone_no,
            id_type=_get_enum_val(db, norm_id_type(d.id_type)),
            id_number=d.id_number,
            designation_id=d.designation_id,
            year_joined=d.year_joined,
            salary=d.salary,
        )
        db.add(emp)
        emps.append(emp)
    if errs:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Validation errors: {'; '.join(errs)}")
    try:
        db.commit()
        for e in emps:
            db.refresh(e)
        return emps
    except Exception as e:
        db.rollback()
        _handle_db_err(e)
