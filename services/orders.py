from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from database.models import PurchaseOrder, POItem, SupplyOrder, SOItem, Project
from models.orders import POCreate, SOCreate


def _po_dict(po: PurchaseOrder, db: Session) -> dict:
    proj = db.query(Project).filter(Project.project_id == po.project_id).first() if po.project_id else None
    items = db.query(POItem).filter(POItem.po_id == po.id).all()
    return {
        "id": po.id,
        "po_number": po.po_number,
        "project_id": po.project_id,
        "project_name": proj.name if proj else None,
        "created_at": po.created_at,
        "items": [{"id": i.id, "size": i.size, "quantity": i.quantity} for i in items],
    }


def _so_dict(so: SupplyOrder, db: Session) -> dict:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == so.po_id).first()
    proj = db.query(Project).filter(Project.project_id == po.project_id).first() if po and po.project_id else None
    items = db.query(SOItem).filter(SOItem.so_id == so.id).all()
    return {
        "id": so.id,
        "po_id": so.po_id,
        "po_number": po.po_number if po else "",
        "invoice_number": so.invoice_number,
        "project_name": proj.name if proj else None,
        "created_at": so.created_at,
        "items": [{"id": i.id, "size": i.size, "supplied_qty": i.supplied_qty, "balance_qty": i.balance_qty} for i in items],
    }


def create_po(data: POCreate, db: Session) -> dict:
    if not data.po_number.strip():
        raise HTTPException(400, "PO number is required")
    if db.query(PurchaseOrder).filter(PurchaseOrder.po_number == data.po_number).first():
        raise HTTPException(400, "PO number already exists")
    if not data.items:
        raise HTTPException(400, "At least one size/quantity is required")
    po = PurchaseOrder(po_number=data.po_number.strip(), project_id=data.project_id)
    db.add(po)
    db.flush()
    for item in data.items:
        db.add(POItem(po_id=po.id, size=item.size, quantity=item.quantity))
    db.commit()
    db.refresh(po)
    return _po_dict(po, db)


def list_pos(db: Session) -> List[dict]:
    pos = db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).all()
    return [_po_dict(po, db) for po in pos]


def get_po(po_id: int, db: Session) -> dict:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "PO not found")
    return _po_dict(po, db)


def list_pos_by_project(project_id: int, db: Session) -> List[dict]:
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.project_id == project_id).order_by(PurchaseOrder.id.desc()).all()
    return [_po_dict(po, db) for po in pos]


def list_standalone_pos(db: Session) -> List[dict]:
    pos = db.query(PurchaseOrder).filter(PurchaseOrder.project_id == None).order_by(PurchaseOrder.id.desc()).all()
    return [_po_dict(po, db) for po in pos]


def get_po_summary(po_id: int, db: Session, exclude_so_id: int = None) -> List[dict]:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "PO not found")
    po_items = db.query(POItem).filter(POItem.po_id == po_id).all()
    q = db.query(SupplyOrder.id).filter(SupplyOrder.po_id == po_id)
    if exclude_so_id:
        q = q.filter(SupplyOrder.id != exclude_so_id)
    so_ids = [s.id for s in q.all()]
    result = []
    for item in po_items:
        total_supplied = 0
        if so_ids:
            total_supplied = db.query(func.sum(SOItem.supplied_qty)).filter(
                SOItem.so_id.in_(so_ids), SOItem.size == item.size
            ).scalar() or 0
        result.append({
            "size": item.size,
            "po_qty": item.quantity,
            "total_supplied": int(total_supplied),
            "balance": item.quantity - int(total_supplied),
        })
    return result


def update_po(po_id: int, data: POCreate, db: Session) -> dict:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "PO not found")
    clash = db.query(PurchaseOrder).filter(PurchaseOrder.po_number == data.po_number.strip(), PurchaseOrder.id != po_id).first()
    if clash:
        raise HTTPException(400, "PO number already exists")
    if not data.items:
        raise HTTPException(400, "At least one size/quantity is required")
    po.po_number = data.po_number.strip()
    po.project_id = data.project_id
    db.query(POItem).filter(POItem.po_id == po_id).delete()
    for item in data.items:
        db.add(POItem(po_id=po.id, size=item.size, quantity=item.quantity))
    db.commit()
    db.refresh(po)
    return _po_dict(po, db)


def delete_po(po_id: int, db: Session) -> dict:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(404, "PO not found")
    db.delete(po)
    db.commit()
    return {"message": "Deleted"}


def update_so(so_id: int, data: SOCreate, db: Session) -> dict:
    so = db.query(SupplyOrder).filter(SupplyOrder.id == so_id).first()
    if not so:
        raise HTTPException(404, "SO not found")
    if not data.items:
        raise HTTPException(400, "At least one item is required")
    so.invoice_number = data.invoice_number or None
    db.query(SOItem).filter(SOItem.so_id == so_id).delete()
    for item in data.items:
        db.add(SOItem(so_id=so.id, size=item.size, supplied_qty=item.supplied_qty, balance_qty=item.balance_qty))
    db.commit()
    db.refresh(so)
    return _so_dict(so, db)


def delete_so(so_id: int, db: Session) -> dict:
    so = db.query(SupplyOrder).filter(SupplyOrder.id == so_id).first()
    if not so:
        raise HTTPException(404, "SO not found")
    db.delete(so)
    db.commit()
    return {"message": "Deleted"}


def create_so(data: SOCreate, db: Session) -> dict:
    if not db.query(PurchaseOrder).filter(PurchaseOrder.id == data.po_id).first():
        raise HTTPException(404, "PO not found")
    if not data.items:
        raise HTTPException(400, "At least one item is required")
    so = SupplyOrder(po_id=data.po_id, invoice_number=data.invoice_number or None)
    db.add(so)
    db.flush()
    for item in data.items:
        db.add(SOItem(so_id=so.id, size=item.size, supplied_qty=item.supplied_qty, balance_qty=item.balance_qty))
    db.commit()
    db.refresh(so)
    return _so_dict(so, db)


def list_sos(db: Session) -> List[dict]:
    sos = db.query(SupplyOrder).order_by(SupplyOrder.id.desc()).all()
    return [_so_dict(so, db) for so in sos]
