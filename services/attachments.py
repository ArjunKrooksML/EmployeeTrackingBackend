import uuid
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database.models import TaskAttachment, Task
import services.storage as storage


def _fmt(a: TaskAttachment):
    return {
        "id": a.id,
        "file_name": a.file_name,
        "url": storage.signed_url(a.storage_path),
        "uploaded_at": a.uploaded_at.isoformat() if a.uploaded_at else None,
    }


def upload_att(task_id: int, file: UploadFile, db: Session):
    if not db.query(Task).filter(Task.task_id == task_id).first():
        raise HTTPException(404, "Task not found")
    data = file.file.read()
    path = f"tasks/{task_id}/{uuid.uuid4().hex}_{file.filename}"
    storage.upload(path, data, file.content_type or 'application/octet-stream')
    att = TaskAttachment(task_id=task_id, file_name=file.filename, storage_path=path)
    db.add(att)
    db.commit()
    db.refresh(att)
    return _fmt(att)


def get_atts(task_id: int, db: Session):
    return [_fmt(a) for a in db.query(TaskAttachment).filter(TaskAttachment.task_id == task_id).all()]


def delete_att(att_id: int, task_id: int, db: Session):
    att = db.query(TaskAttachment).filter(
        TaskAttachment.id == att_id,
        TaskAttachment.task_id == task_id,
    ).first()
    if not att:
        raise HTTPException(404, "Attachment not found")
    storage.delete(att.storage_path)
    db.delete(att)
    db.commit()
    return {"message": "Deleted"}
