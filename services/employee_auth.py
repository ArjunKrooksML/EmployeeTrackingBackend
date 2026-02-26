from fastapi import HTTPException
from sqlalchemy.orm import Session

from database.models import Employee as EmployeeDB
from middleware.helpers import verify_password
from models.employees import EmployeeLogin, EmployeePublic


def authenticate_employee(credentials: EmployeeLogin, db: Session) -> EmployeePublic:
    employee = db.query(EmployeeDB).filter(EmployeeDB.email == credentials.email).first()
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(credentials.password, employee.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return EmployeePublic.model_validate(employee)

