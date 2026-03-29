from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database.connection import get_db
from models.attendance import AttResp, AttWithEmp, AttUpdate
from middleware.rbac import require_gm
from services import attendance as svc

router = APIRouter()


@router.post("/attendance/checkin", response_model=AttResp)
def checkin(
    employee_id: int = Query(...),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    return svc.do_checkin(employee_id, db, lat, lng)


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
