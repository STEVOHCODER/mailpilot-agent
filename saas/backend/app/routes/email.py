from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, EmailConnection
from app.schemas import EmailConnect, EmailConnectionResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/email", tags=["email"])


@router.get("/connections", response_model=list[EmailConnectionResponse])
def list_connections(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conns = db.query(EmailConnection).filter(EmailConnection.user_id == user.id).all()
    return [EmailConnectionResponse.model_validate(c) for c in conns]


@router.post("/connect", response_model=EmailConnectionResponse)
def connect_email(
    data: EmailConnect,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(EmailConnection)
        .filter(EmailConnection.user_id == user.id, EmailConnection.email_address == data.email_address.lower())
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already connected")

    conn = EmailConnection(
        user_id=user.id,
        provider=data.provider,
        email_address=data.email_address.lower(),
        encrypted_token=data.password,  # TODO: encrypt properly
        imap_host=data.imap_host,
        imap_port=data.imap_port,
    )
    db.add(conn)
    db.commit()
    db.refresh(conn)
    return EmailConnectionResponse.model_validate(conn)


@router.delete("/connections/{connection_id}")
def disconnect_email(
    connection_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conn = (
        db.query(EmailConnection)
        .filter(EmailConnection.id == connection_id, EmailConnection.user_id == user.id)
        .first()
    )
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    db.delete(conn)
    db.commit()
    return {"ok": True}
