import json
import datetime
from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Employee as EmpDB
from middleware.auth import get_current_employee
from services import expenses as svc

router = APIRouter(prefix="/expenses", tags=["expenses"])

MAX_BYTES = 25 * 1024 * 1024  # 25 MB


@router.get("/mine")
def my_expenses(emp: EmpDB = Depends(get_current_employee), db: Session = Depends(get_db)):
    return svc.my(emp.employee_id, db)


@router.post("")
async def create_expense(
    title: str = Form(...),
    date: str = Form(...),
    date_to: Optional[str] = Form(None),
    items: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    emp: EmpDB = Depends(get_current_employee),
    db: Session = Depends(get_db),
):
    try:
        items_list = json.loads(items)
    except Exception:
        raise HTTPException(400, "Invalid items JSON")
    try:
        d = datetime.date.fromisoformat(date)
    except Exception:
        raise HTTPException(400, "Invalid date")
    dt = datetime.date.fromisoformat(date_to) if date_to else None

    file_data = []
    total_bytes = 0
    for f in files:
        if not f.filename:
            continue
        data = await f.read()
        total_bytes += len(data)
        if total_bytes > MAX_BYTES:
            raise HTTPException(400, "Total attachment size exceeds 25 MB")
        file_data.append((f.filename, data, f.content_type or 'application/octet-stream'))

    return await svc.create(emp.employee_id, title, d, items_list, file_data, dt, db)
