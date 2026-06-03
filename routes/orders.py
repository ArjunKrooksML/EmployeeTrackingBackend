from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from services import orders as svc
from models.orders import POCreate, SOCreate, POResponse, SOResponse, POSizeSummary

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/po", response_model=List[POResponse])
def list_pos(db: Session = Depends(get_db)):
    return svc.list_pos(db)


@router.post("/po", response_model=POResponse)
def create_po(data: POCreate, db: Session = Depends(get_db)):
    return svc.create_po(data, db)


@router.get("/po/standalone", response_model=List[POResponse])
def standalone_pos(db: Session = Depends(get_db)):
    return svc.list_standalone_pos(db)


@router.get("/po/by-project/{project_id}", response_model=List[POResponse])
def pos_by_project(project_id: int, db: Session = Depends(get_db)):
    return svc.list_pos_by_project(project_id, db)


@router.get("/po/{po_id}/summary", response_model=List[POSizeSummary])
def po_summary(po_id: int, exclude_so: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return svc.get_po_summary(po_id, db, exclude_so_id=exclude_so)


@router.get("/po/{po_id}", response_model=POResponse)
def get_po(po_id: int, db: Session = Depends(get_db)):
    return svc.get_po(po_id, db)


@router.put("/po/{po_id}", response_model=POResponse)
def update_po(po_id: int, data: POCreate, db: Session = Depends(get_db)):
    return svc.update_po(po_id, data, db)


@router.delete("/po/{po_id}")
def delete_po(po_id: int, db: Session = Depends(get_db)):
    return svc.delete_po(po_id, db)


@router.get("/so", response_model=List[SOResponse])
def list_sos(db: Session = Depends(get_db)):
    return svc.list_sos(db)


@router.post("/so", response_model=SOResponse)
def create_so(data: SOCreate, db: Session = Depends(get_db)):
    return svc.create_so(data, db)


@router.put("/so/{so_id}", response_model=SOResponse)
def update_so(so_id: int, data: SOCreate, db: Session = Depends(get_db)):
    return svc.update_so(so_id, data, db)


@router.delete("/so/{so_id}")
def delete_so(so_id: int, db: Session = Depends(get_db)):
    return svc.delete_so(so_id, db)
