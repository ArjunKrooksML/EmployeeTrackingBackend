from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.connection import get_db
from models.admin import AdminLogin
import services.auth as auth_service
from services.auth import auth_admin, refresh_access_token

router = APIRouter(prefix="/admin/auth", tags=["admin/auth"])


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/login")
async def login(payload: AdminLogin, db: Session = Depends(get_db)):
    return auth_admin(payload, db)
@router.post("/refresh")
async def refresh(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_access_token(req.refresh_token, db)


class ResetPasswordReq(BaseModel):
    email: str
    otp: str
    new_password: str

@router.post("/reset-password")
async def reset_pwd(req: ResetPasswordReq, db: Session = Depends(get_db)):
    return auth_service.reset_password(req.email, req.otp, req.new_password, "admin", db)


class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

from middleware.auth import get_current_admin
from database.models import Admin as AdminDB

@router.post("/change-password")
async def change_pwd(req: ChangePasswordReq, admin: AdminDB = Depends(get_current_admin), db: Session = Depends(get_db)):
    return auth_service.change_password(admin.id, req.old_password, req.new_password, "admin", db)

