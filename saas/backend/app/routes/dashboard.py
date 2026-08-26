from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import User, EmailConnection, WhatsAppConnection, MessageLog, Subscription, Usage
from app.schemas import DashboardResponse, MessageLogResponse, SubscriptionResponse, UsageResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today_start.replace(day=1)

    email_count = db.query(EmailConnection).filter(EmailConnection.user_id == user.id, EmailConnection.is_active == True).count()
    whatsapp = db.query(WhatsAppConnection).filter(WhatsAppConnection.user_id == user.id).first()
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()

    today_count = (
        db.query(func.count(MessageLog.id))
        .filter(MessageLog.user_id == user.id, MessageLog.created_at >= today_start)
        .scalar()
    )
    month_count = (
        db.query(func.count(MessageLog.id))
        .filter(MessageLog.user_id == user.id, MessageLog.created_at >= month_start)
        .scalar()
    )

    recent = (
        db.query(MessageLog)
        .filter(MessageLog.user_id == user.id)
        .order_by(MessageLog.created_at.desc())
        .limit(20)
        .all()
    )

    return DashboardResponse(
        status="active" if whatsapp and whatsapp.is_active else "inactive",
        email_connections=email_count,
        whatsapp_connected=whatsapp is not None and whatsapp.is_active,
        messages_today=today_count,
        messages_this_month=month_count,
        plan=sub.plan if sub else "free",
        recent_messages=[MessageLogResponse.model_validate(m) for m in recent],
    )


@router.get("/messages", response_model=list[MessageLogResponse])
def list_messages(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    msgs = (
        db.query(MessageLog)
        .filter(MessageLog.user_id == user.id)
        .order_by(MessageLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [MessageLogResponse.model_validate(m) for m in msgs]


@router.get("/subscription", response_model=SubscriptionResponse)
def get_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    usage = db.query(Usage).filter(Usage.user_id == user.id).first()

    limits = {"free": 100, "starter": 1000, "pro": 5000, "business": 20000}
    plan_limit = limits.get(sub.plan if sub else "free", 100)

    return SubscriptionResponse(
        plan=sub.plan if sub else "free",
        status=sub.status if sub else "active",
        current_period_end=sub.current_period_end if sub else None,
        emails_limit=plan_limit,
        emails_used=usage.messages_forwarded if usage else 0,
    )


@router.get("/usage", response_model=UsageResponse)
def get_usage(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usage = db.query(Usage).filter(Usage.user_id == user.id).first()
    if not usage:
        return UsageResponse(
            emails_received=0, emails_processed=0,
            messages_forwarded=0, messages_failed=0,
            period_start=None, period_end=None,
        )
    return UsageResponse.model_validate(usage)
