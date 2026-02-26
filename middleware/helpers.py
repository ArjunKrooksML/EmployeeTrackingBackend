import re
from typing import Optional
import hashlib
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException

def val_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def val_pwd(pwd: str, min_len: int = 6, max_len: int = 100) -> bool:
    return bool(pwd and min_len <= len(pwd) <= max_len)

def val_phone(phone: str) -> bool:
    return bool(re.match(r'^[0-9]{10,15}$', phone.replace(' ', '').replace('-', '')))

def val_date(date_str: str) -> bool:
    try:
        from datetime import datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False

def val_id(id_num: str, id_type: Optional[str] = None) -> bool:
    if not id_num:
        return False
    id_clean = id_num.strip()
    if not id_clean.isdigit():
        return False
    if id_type:
        id_lower = id_type.lower()
        if id_lower in ['aadhaar', 'aadhar']:
            return len(id_clean) == 12
        elif id_lower == 'pan':
            return len(id_clean) == 10
        elif id_lower == 'passport':
            return len(id_clean) == 8
    return len(id_clean) <= 50

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def verify_pwd(plain: str, hashed: str) -> bool:
    return hash_pwd(plain) == hashed

def val_desig_id(desig_id: Optional[int], db: Session) -> None:
    if desig_id is not None:
        try:
            result = db.execute(text("SELECT 1 FROM designations WHERE id = :id"), {"id": desig_id})
            if not result.first():
                raise HTTPException(status_code=400, detail=f"Designation ID {desig_id} does not exist")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error validating designation_id: {str(e)}")

# Backward compatibility aliases
validate_email = val_email
validate_password = val_pwd
validate_phone = val_phone
validate_date = val_date
validate_id_number = val_id
hash_password = hash_pwd
verify_password = verify_pwd
validate_designation_id = val_desig_id

