from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, Subscription, EmailConnection, WhatsAppConnection, MessageLog, Usage
from app.auth import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def get_stats(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    return {
        "total_users": db.query(func.count(User.id)).scalar(),
        "active_users": db.query(func.count(User.id)).filter(User.is_active == True).scalar(),
        "total_email_connections": db.query(func.count(EmailConnection.id)).filter(EmailConnection.is_active == True).scalar(),
        "total_whatsapp_connections": db.query(func.count(WhatsAppConnection.id)).filter(WhatsAppConnection.is_active == True).scalar(),
        "total_messages": db.query(func.count(MessageLog.id)).scalar(),
        "messages_forwarded": db.query(func.count(MessageLog.id)).filter(MessageLog.forwarded == True).scalar(),
        "messages_failed": db.query(func.count(MessageLog.id)).filter(MessageLog.delivery_status == "failed").scalar(),
        "plans": dict(db.query(Subscription.plan, func.count(Subscription.id)).group_by(Subscription.plan).all()),
    }


@router.get("/users")
def list_users(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        sub = db.query(Subscription).filter(Subscription.user_id == u.id).first()
        usage = db.query(Usage).filter(Usage.user_id == u.id).first()
        result.append({
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "is_active": u.is_active,
            "plan": sub.plan if sub else "free",
            "messages_forwarded": usage.messages_forwarded if usage else 0,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return result


@router.post("/users/{user_id}/toggle")
def toggle_user(user_id: str, admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "not found"}
    user.is_active = not user.is_active
    db.commit()
    return {"ok": True, "is_active": user.is_active}
