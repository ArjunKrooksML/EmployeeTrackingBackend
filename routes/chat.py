from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from middleware.auth import get_current_admin, get_current_employee
from services.chat_service import chat_employee, chat_admin

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    messages: list[dict]  # [{"role": "user"|"assistant", "content": "..."}]


@router.post("/employees/chat")
def emp_chat(req: ChatRequest, emp=Depends(get_current_employee), db: Session = Depends(get_db)):
    reply = chat_employee(req.messages, emp, db)
    return {"reply": reply}


@router.post("/admin/chat")
def admin_chat(req: ChatRequest, admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    reply = chat_admin(req.messages, admin, db)
    return {"reply": reply}
