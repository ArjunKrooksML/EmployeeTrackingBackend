from fastapi import HTTPException
from sqlalchemy.orm import Session
from middleware.helpers import verify_pwd, hash_pwd
from middleware.jwt import create_tokens, verify_token, create_access_token
from database.models import Admin as AdminDB, Employee as EmpDB
from models.admin import AdminLogin, AdminPublic
from models.employees import EmployeeLogin, EmployeePublic
from services.otp import gen_otp, verify_otp
from services.email import send_otp_email


def auth_admin(creds: AdminLogin, db: Session) -> dict:
    # Validate admin credentials and return tokens
    admin = db.query(AdminDB).filter(AdminDB.email == creds.email).first()
    if not admin or not verify_pwd(creds.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access, refresh = create_tokens({"admin_id": admin.id, "email": admin.email, "type": "admin"})
    return {"access_token": access, "refresh_token": refresh, "user": AdminPublic.model_validate(admin)}


def auth_emp(creds: EmployeeLogin, db: Session) -> dict:
    # Validate employee credentials and return tokens
    emp = db.query(EmpDB).filter(EmpDB.email == creds.email).first()
    if not emp or not verify_pwd(creds.password, emp.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access, refresh = create_tokens({"employee_id": emp.employee_id, "email": emp.email, "type": "employee"})
    return {"access_token": access, "refresh_token": refresh, "user": EmployeePublic.model_validate(emp)}


def refresh_tok(refresh_token: str, db: Session) -> dict:
    # Generate new access token from a valid refresh token
    payload = verify_token(refresh_token, token_type="refresh")
    utype = payload.get("type")
    if utype == "admin":
        aid = payload.get("admin_id")
        if not aid:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        admin = db.query(AdminDB).filter(AdminDB.id == aid).first()
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        tok = create_access_token({"admin_id": admin.id, "email": admin.email, "type": "admin"})
        return {"access_token": tok, "user": AdminPublic.model_validate(admin)}
    elif utype == "employee":
        eid = payload.get("employee_id")
        if not eid:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        emp = db.query(EmpDB).filter(EmpDB.employee_id == eid).first()
        if not emp:
            raise HTTPException(status_code=401, detail="Employee not found")
        tok = create_access_token({"employee_id": emp.employee_id, "email": emp.email, "type": "employee"})
        return {"access_token": tok, "user": EmployeePublic.model_validate(emp)}
    raise HTTPException(status_code=401, detail="Invalid token type")


def send_reset_otp(email: str, utype: str, db: Session) -> dict:
    if utype == "admin":
        u = db.query(AdminDB).filter(AdminDB.email == email).first()
    else:
        u = db.query(EmpDB).filter(EmpDB.email == email).first()
    if not u:
        # Don't reveal whether email exists
        return {"message": "If that email exists, an OTP has been sent"}
    otp = gen_otp(email, db)
    send_otp_email(email, otp)
    return {"message": "If that email exists, an OTP has been sent"}


def reset_pwd(email: str, otp: str, new_pwd: str, utype: str, db: Session) -> dict:
    # Reset password after OTP validation
    if not verify_otp(email, otp, db):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    hashed = hash_pwd(new_pwd)
    if utype == "admin":
        u = db.query(AdminDB).filter(AdminDB.email == email).first()
    elif utype == "employee":
        u = db.query(EmpDB).filter(EmpDB.email == email).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.password = hashed
    db.commit()
    return {"message": "Password reset successfully"}


def change_pwd(user_id: int, old_pwd: str, new_pwd: str, utype: str, db: Session) -> dict:
    # Change password after verifying old password
    if utype == "admin":
        u = db.query(AdminDB).filter(AdminDB.id == user_id).first()
    elif utype == "employee":
        u = db.query(EmpDB).filter(EmpDB.employee_id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_pwd(old_pwd, u.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    u.password = hash_pwd(new_pwd)
    db.commit()
    return {"message": "Password changed successfully"}
