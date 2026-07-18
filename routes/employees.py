from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connection import get_db
from middleware.auth import get_current_employee
from database.models import Employee as EmpDB
from models.employees import EmployeeLogin
from services.auth import auth_emp, refresh_tok, reset_pwd, change_pwd, send_reset_otp, logout_user
import services.profile as profile_svc
import services.id_card as id_card_svc

router = APIRouter(prefix="/employees", tags=["employees"])


class RefreshReq(BaseModel):
    refresh_token: str


class SendOtpReq(BaseModel):
    email: str


class ResetReq(BaseModel):
    email: str
    otp: str
    new_password: str


class ChangePwdReq(BaseModel):
    old_password: str
    new_password: str


@router.post("/login")
async def login(payload: EmployeeLogin, db: Session = Depends(get_db)):
    return auth_emp(payload, db)


@router.post("/refresh")
async def refresh(req: RefreshReq, db: Session = Depends(get_db)):
    return refresh_tok(req.refresh_token, db)


@router.post("/send-otp")
async def send_otp(req: SendOtpReq, db: Session = Depends(get_db)):
    return send_reset_otp(req.email, "employee", db)


@router.post("/reset-password")
async def reset_password(req: ResetReq, db: Session = Depends(get_db)):
    return reset_pwd(req.email, req.otp, req.new_password, "employee", db)


@router.post("/logout")
async def logout(req: RefreshReq, db: Session = Depends(get_db)):
    return logout_user(req.refresh_token, db)


@router.post("/change-password")
async def change_password(req: ChangePwdReq, emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return change_pwd(emp.employee_id, req.old_password, req.new_password, "employee", db)


@router.post("/profile-picture")
async def upload_profile_picture(file: UploadFile = File(...), emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return await profile_svc.set_pic(emp, file, db)


@router.delete("/profile-picture")
async def remove_profile_picture(emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return profile_svc.remove_pic(emp, db)


@router.get("/id-card")
async def get_id_card(emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    png = await id_card_svc.build_card(emp)
    return Response(content=png, media_type="image/png", headers={"Content-Disposition": 'inline; filename="id_card.png"'})
