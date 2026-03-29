from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.jwt import verify_token
from database.models import Admin as AdminDB, Employee as EmpDB

_sec = HTTPBearer()

_HR_GM = {'hr', 'gm'}
_GM_ONLY = {'gm'}


def _get_payload(creds: HTTPAuthorizationCredentials):
    # Decode token without enforcing user type yet
    return verify_token(creds.credentials, token_type="access")


def require_hr_or_gm(
    creds: HTTPAuthorizationCredentials = Depends(_sec),
    db: Session = Depends(get_db)
):
    # Admin tokens always pass through
    payload = _get_payload(creds)
    if payload.get("admin_id"):
        admin = db.query(AdminDB).filter(AdminDB.id == payload["admin_id"]).first()
        if admin:
            return admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    # Employee tokens must have hr or gm role
    emp_id = payload.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Employee not found")
    if emp.role not in _HR_GM:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return emp


def require_gm(
    creds: HTTPAuthorizationCredentials = Depends(_sec),
    db: Session = Depends(get_db)
):
    # Admin tokens always pass through
    payload = _get_payload(creds)
    if payload.get("admin_id"):
        admin = db.query(AdminDB).filter(AdminDB.id == payload["admin_id"]).first()
        if admin:
            return admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    # Employee tokens must have gm role
    emp_id = payload.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Employee not found")
    if emp.role not in _GM_ONLY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return emp
