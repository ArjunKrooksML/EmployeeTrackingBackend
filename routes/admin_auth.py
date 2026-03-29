from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connection import get_db
from middleware.auth import get_current_admin
from database.models import Admin as AdminDB
from models.admin import AdminLogin
from services.auth import auth_admin, refresh_tok, reset_pwd, change_pwd

router = APIRouter(prefix="/admin/auth", tags=["admin/auth"])


class RefreshReq(BaseModel):
    refresh_token: str


class ResetReq(BaseModel):
    email: str
    otp: str
    new_password: str


class ChangePwdReq(BaseModel):
    old_password: str
    new_password: str


@router.post("/login")
async def login(payload: AdminLogin, db: Session = Depends(get_db)):
    return auth_admin(payload, db)


@router.post("/refresh")
async def refresh(req: RefreshReq, db: Session = Depends(get_db)):
    return refresh_tok(req.refresh_token, db)


@router.post("/reset-password")
async def reset_password(req: ResetReq, db: Session = Depends(get_db)):
    return reset_pwd(req.email, req.otp, req.new_password, "admin", db)


@router.post("/change-password")
async def change_password(req: ChangePwdReq, admin: AdminDB = Depends(get_current_admin), db: Session = Depends(get_db)):
    return change_pwd(admin.id, req.old_password, req.new_password, "admin", db)
