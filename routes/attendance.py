from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database.connection import get_db
from models.attendance import AttResp, AttWithEmp, AttUpdate, CheckinReq
from middleware.rbac import require_gm
from services import attendance as svc

router = APIRouter()


@router.post("/attendance/checkin", response_model=AttResp)
def checkin(data: CheckinReq, db: Session = Depends(get_db)):
    return svc.do_checkin(data.employee_id, db, data.lat, data.lng)


@router.get("/attendance/employee/{employee_id}", response_model=List[AttResp])
def my_att(employee_id: int, db: Session = Depends(get_db)):
    return svc.get_att(employee_id, db)


@router.get("/attendance/all", response_model=List[AttWithEmp])
def att_all(db: Session = Depends(get_db), _: None = Depends(require_gm)):
    # GM only: view all attendance records
    return svc.all_att(db)


@router.put("/attendance/{att_id}", response_model=AttResp)
def upd_att(att_id: int, data: AttUpdate, db: Session = Depends(get_db)):
    return svc.upd_att(att_id, data, db)
