from fastapi import HTTPException
from sqlalchemy.orm import Session
from middleware.helpers import verify_pwd, hash_pwd
from middleware.jwt import create_tokens, verify_token, create_access_token
from database.models import Admin as AdminDB, Employee as EmployeeDB
from models.admin import AdminLogin, AdminPublic
from models.employees import EmployeeLogin, EmployeePublic


def auth_admin(creds: AdminLogin, db: Session) -> dict:
    admin = db.query(AdminDB).filter(AdminDB.email == creds.email).first()
    if not admin or not verify_pwd(creds.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token, refresh_token = create_tokens({"admin_id": admin.id, "email": admin.email, "type": "admin"})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": AdminPublic.model_validate(admin)
    }


def auth_emp(creds: EmployeeLogin, db: Session) -> dict:
    emp = db.query(EmployeeDB).filter(EmployeeDB.email == creds.email).first()
    if not emp or not verify_pwd(creds.password, emp.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token, refresh_token = create_tokens({"employee_id": emp.employee_id, "email": emp.email, "type": "employee"})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": EmployeePublic.model_validate(emp)
    }


def refresh_access_token(refresh_token: str, db: Session) -> dict:
    """Generate new access token from refresh token"""
    payload = verify_token(refresh_token, token_type="refresh")
    
    user_type = payload.get("type")
    if user_type == "admin":
        admin_id = payload.get("admin_id")
        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        admin = db.query(AdminDB).filter(AdminDB.id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=401, detail="Admin not found")
        new_access_token = create_access_token({"admin_id": admin.id, "email": admin.email, "type": "admin"})
        return {"access_token": new_access_token, "user": AdminPublic.model_validate(admin)}
    
    elif user_type == "employee":
        emp_id = payload.get("employee_id")
        if not emp_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        emp = db.query(EmployeeDB).filter(EmployeeDB.employee_id == emp_id).first()
        if not emp:
            raise HTTPException(status_code=401, detail="Employee not found")
        new_access_token = create_access_token({"employee_id": emp.employee_id, "email": emp.email, "type": "employee"})
        return {"access_token": new_access_token, "user": EmployeePublic.model_validate(emp)}
    
    raise HTTPException(status_code=401, detail="Invalid token type")


def reset_password(email: str, otp: str, new_pwd: str, user_type: str, db: Session) -> dict:
    if otp != "1234":
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    hashed_pwd = hash_pwd(new_pwd)
    
    if user_type == "admin":
        user = db.query(AdminDB).filter(AdminDB.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password = hashed_pwd
    elif user_type == "employee":
        user = db.query(EmployeeDB).filter(EmployeeDB.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.password = hashed_pwd
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")
    
    db.commit()
    return {"message": "Password reset successfully"}


def change_password(user_id: int, old_pwd: str, new_pwd: str, user_type: str, db: Session) -> dict:
    if user_type == "admin":
        user = db.query(AdminDB).filter(AdminDB.id == user_id).first()
    elif user_type == "employee":
        user = db.query(EmployeeDB).filter(EmployeeDB.employee_id == user_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_pwd(old_pwd, user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    user.password = hash_pwd(new_pwd)
    db.commit()
    return {"message": "Password changed successfully"}

