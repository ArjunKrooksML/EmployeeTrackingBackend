from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.jwt import verify_token
from database.models import Admin as AdminDB, Employee as EmpDB

_sec = HTTPBearer()

_HR_GM = {'hr', 'gm'}
_GM_ONLY = {'gm'}
_GM_SENIOR = {'gm', 'senior'}
_HR_GM_SENIOR = {'hr', 'gm', 'senior'}


def _resolve(creds: HTTPAuthorizationCredentials, db: Session, allowed: set | None = None):
    payload = verify_token(creds.credentials, token_type="access")
    if payload.get("admin_id"):
        admin = db.query(AdminDB).filter(AdminDB.id == payload["admin_id"]).first()
        if admin:
            return admin
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    emp_id = payload.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    emp = db.query(EmpDB).filter(EmpDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Employee not found")
    if allowed and emp.role not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return emp


def require_any_user(creds: HTTPAuthorizationCredentials = Depends(_sec), db: Session = Depends(get_db)):
    return _resolve(creds, db)

def require_hr_or_gm(creds: HTTPAuthorizationCredentials = Depends(_sec), db: Session = Depends(get_db)):
    return _resolve(creds, db, _HR_GM)

def require_gm(creds: HTTPAuthorizationCredentials = Depends(_sec), db: Session = Depends(get_db)):
    return _resolve(creds, db, _GM_ONLY)

def require_hr_gm_or_senior(creds: HTTPAuthorizationCredentials = Depends(_sec), db: Session = Depends(get_db)):
    return _resolve(creds, db, _HR_GM_SENIOR)

def require_gm_or_senior(creds: HTTPAuthorizationCredentials = Depends(_sec), db: Session = Depends(get_db)):
    return _resolve(creds, db, _GM_SENIOR)
