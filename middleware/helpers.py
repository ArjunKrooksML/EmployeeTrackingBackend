import re
from typing import Optional
import hashlib
import bcrypt
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
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def verify_pwd(plain: str, hashed: str) -> bool:
    # Support bcrypt hashes (new) and legacy SHA256 hashes (migration path)
    if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
        try:
            return bcrypt.checkpw(plain.encode(), hashed.encode())
        except Exception:
            return False
    # Legacy SHA256 — still lets existing accounts log in
    return hashlib.sha256(plain.encode()).hexdigest() == hashed


# Backward compatibility aliases
validate_email = val_email
validate_password = val_pwd
validate_phone = val_phone
validate_date = val_date
validate_id_number = val_id
hash_password = hash_pwd
verify_password = verify_pwd

