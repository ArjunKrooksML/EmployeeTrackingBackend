from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connection import get_db
from models.employees import EmployeeLogin
from services.auth import auth_emp, refresh_access_token
import services.auth

router = APIRouter(prefix="/employees", tags=["employees"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(payload: EmployeeLogin, db: Session = Depends(get_db)):
    return auth_emp(payload, db)
@router.post("/refresh")
async def refresh(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_access_token(req.refresh_token, db)


class ResetPasswordReq(BaseModel):
    email: str
    otp: str
    new_password: str

@router.post("/reset-password")
async def reset_pwd(req: ResetPasswordReq, db: Session = Depends(get_db)):
    return services.auth.reset_password(req.email, req.otp, req.new_password, "employee", db)


class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

from middleware.auth import get_current_employee
from database.models import Employee as EmployeeDB

@router.post("/change-password")
async def change_pwd(req: ChangePasswordReq, employee: EmployeeDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return services.auth.change_password(employee.employee_id, req.old_password, req.new_password, "employee", db)
