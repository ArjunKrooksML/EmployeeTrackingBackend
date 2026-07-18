import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from database.models import Employee
import services.storage as storage

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 5 * 1024 * 1024


async def set_pic(emp: Employee, file: UploadFile, db: Session) -> dict:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Only JPEG, PNG or WEBP images are allowed")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "Image must be under 5MB")
    ext = file.filename.rsplit('.', 1)[-1].lower() if file.filename and '.' in file.filename else 'jpg'
    path = f"profile/{emp.employee_id}/{uuid.uuid4().hex}.{ext}"
    storage.upload(path, data, file.content_type)
    old = emp.profile_pic_path
    emp.profile_pic_path = path
    db.commit()
    if old:
        try:
            storage.delete(old)
        except Exception:
            pass
    return {"profile_pic_url": storage.signed_url(path)}


def remove_pic(emp: Employee, db: Session) -> dict:
    if emp.profile_pic_path:
        try:
            storage.delete(emp.profile_pic_path)
        except Exception:
            pass
        emp.profile_pic_path = None
        db.commit()
    return {"message": "Profile picture removed"}
