from fastapi import HTTPException
from sqlalchemy.orm import Session

from database.models import Admin as AdminDB
from middleware.helpers import verify_password
from models.admin import AdminLogin, AdminPublic


def authenticate_admin(credentials: AdminLogin, db: Session) -> AdminPublic:
    admin = db.query(AdminDB).filter(AdminDB.email == credentials.email).first()
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(credentials.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return AdminPublic.model_validate(admin)

