from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.jwt import verify_token
from database.models import Admin as AdminDB, Employee as EmployeeDB

security = HTTPBearer()


def get_current_admin(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminDB:
    payload = verify_token(creds.credentials, token_type="access")
    admin_id = payload.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    admin = db.query(AdminDB).filter(AdminDB.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")
    return admin


def get_current_employee(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> EmployeeDB:
    payload = verify_token(creds.credentials, token_type="access")
    emp_id = payload.get("employee_id")
    if not emp_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Employee not found")
    return emp

