from sqlalchemy.orm import Session
from sqlalchemy import extract
from database.models import Vendor, RawMaterialProcurement
from fastapi import HTTPException
from typing import Optional


def list_vendors(db: Session):
    return db.query(Vendor).order_by(Vendor.name).all()


def create_vendor(name: str, db: Session) -> Vendor:
    name = name.strip()
    if not name:
        raise HTTPException(400, "Vendor name is required")
    if db.query(Vendor).filter(Vendor.name == name).first():
        raise HTTPException(400, "Vendor already exists")
    v = Vendor(name=name)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def update_vendor(vendor_id: int, name: str, db: Session) -> Vendor:
    v = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not v:
        raise HTTPException(404, "Vendor not found")
    name = name.strip()
    if not name:
        raise HTTPException(400, "Vendor name is required")
    if db.query(Vendor).filter(Vendor.name == name, Vendor.id != vendor_id).first():
        raise HTTPException(400, "Vendor already exists")
    v.name = name
    db.commit()
    db.refresh(v)
    return v


def delete_vendor(vendor_id: int, db: Session) -> dict:
    v = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not v:
        raise HTTPException(404, "Vendor not found")
    db.delete(v)
    db.commit()
    return {"message": "Vendor deleted"}


def _vendor_name(vendor_id, db: Session):
    if not vendor_id:
        return None
    v = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    return v.name if v else None


def _fmt(p: RawMaterialProcurement, db: Session) -> dict:
    return {
        "id": p.id, "date": p.date, "bill_no": p.bill_no,
        "vendor_id": p.vendor_id, "vendor_name": _vendor_name(p.vendor_id, db),
        "heat_no": p.heat_no, "tc_no": p.tc_no, "lot_no": p.lot_no, "test_report_no": p.test_report_no,
        "items": p.items if isinstance(p.items, list) else [],
        "uploaded_by": p.uploaded_by, "created_at": p.created_at,
    }


def get_procurements(db: Session, skip: int = 0, limit: int = 20,
                      month: Optional[int] = None, year: Optional[int] = None):
    q = db.query(RawMaterialProcurement).order_by(
        RawMaterialProcurement.date.desc(), RawMaterialProcurement.id.desc())
    if month and year:
        q = q.filter(extract('month', RawMaterialProcurement.date) == month,
                     extract('year', RawMaterialProcurement.date) == year)
    total = q.count()
    rows = q.offset(skip).limit(limit).all()
    return total, [_fmt(p, db) for p in rows]


def create_procurement(data: dict, uploaded_by: str, db: Session) -> dict:
    if not db.query(Vendor).filter(Vendor.id == data["vendor_id"]).first():
        raise HTTPException(404, "Vendor not found")
    p = RawMaterialProcurement(uploaded_by=uploaded_by, **data)
    db.add(p)
    db.commit()
    db.refresh(p)
    return _fmt(p, db)


def update_procurement(procurement_id: int, data: dict, db: Session) -> dict:
    p = db.query(RawMaterialProcurement).filter(RawMaterialProcurement.id == procurement_id).first()
    if not p:
        raise HTTPException(404, "Procurement entry not found")
    if not db.query(Vendor).filter(Vendor.id == data["vendor_id"]).first():
        raise HTTPException(404, "Vendor not found")
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _fmt(p, db)


def delete_procurement(procurement_id: int, db: Session) -> dict:
    p = db.query(RawMaterialProcurement).filter(RawMaterialProcurement.id == procurement_id).first()
    if not p:
        raise HTTPException(404, "Procurement entry not found")
    db.delete(p)
    db.commit()
    return {"message": "Procurement entry deleted"}
