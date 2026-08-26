from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WhatsAppConnection
from app.schemas import WhatsAppConnect, WhatsAppResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


@router.get("/connection", response_model=WhatsAppResponse | None)
def get_connection(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conn = db.query(WhatsAppConnection).filter(WhatsAppConnection.user_id == user.id).first()
    if not conn:
        return None
    return WhatsAppResponse.model_validate(conn)


@router.post("/connect", response_model=WhatsAppResponse)
def connect_whatsapp(
    data: WhatsAppConnect,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(WhatsAppConnection).filter(WhatsAppConnection.user_id == user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="WhatsApp already connected. Disconnect first.")

    conn = WhatsAppConnection(
        user_id=user.id,
        phone_number=data.phone_number,
        meta_phone_number_id=data.meta_phone_number_id,
        meta_access_token=data.meta_access_token,  # TODO: encrypt
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return WhatsAppResponse.model_validate(conn)


@router.delete("/connection")
def disconnect_whatsapp(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conn = db.query(WhatsAppConnection).filter(WhatsAppConnection.user_id == user.id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No WhatsApp connection")
    db.delete(conn)
    db.commit()
    return {"ok": True}


@router.post("/test")
def send_test_message(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conn = db.query(WhatsAppConnection).filter(WhatsAppConnection.user_id == user.id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="No WhatsApp connection")

    import requests as req
    url = f"https://graph.facebook.com/v21.0/{conn.meta_phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": conn.phone_number,
        "type": "text",
        "text": {"body": "MailPilot test message — your WhatsApp connection is working!"},
    }
    resp = req.post(url, headers={"Authorization": f"Bearer {conn.meta_access_token}", "Content-Type": "application/json"}, json=payload, timeout=20)
    if resp.status_code >= 400:
        raise HTTPException(status_code=400, detail=f"Meta API error: {resp.text[:300]}")
    return {"ok": True, "message_id": resp.json().get("messages", [{}])[0].get("id")}
