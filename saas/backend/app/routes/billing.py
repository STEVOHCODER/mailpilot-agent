"""Billing routes — checkout, portal, webhook."""
import os
from fastapi import APIRouter, Request, HTTPException
from app.auth import get_current_user
from app.models import User, Subscription
from app.billing import create_checkout_session, create_portal_session, handle_webhook, PLANS
from app.database import get_db

router = APIRouter(prefix="/api/billing", tags=["billing"])


@router.get("/plans")
def list_plans():
    return [
        {"id": "free", "name": "Free", "price": 0, "messages_day": 25, "features": ["25 msgs/day", "1 email account", "1 rule"]},
        {"id": "pro", "name": "Pro", "price": 10, "messages_day": 250, "features": ["250 msgs/day", "3 email accounts", "10 rules", "Priority support"]},
        {"id": "enterprise", "name": "Enterprise", "price": 49, "messages_day": -1, "features": ["Unlimited msgs", "Unlimited emails", "Unlimited rules", "SLA", "Dedicated support"]},
    ]


@router.get("/subscription")
def get_subscription(user: User = get_current_user()):
    db = next(get_db())
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        return {"plan": "free", "status": "active", "messages_day": 25}
    return {
        "plan": sub.plan,
        "status": sub.status,
        "messages_day": PLANS.get(sub.plan, {}).get("messages_day", 25),
        "current_period_end": str(sub.current_period_end) if sub.current_period_end else None,
    }


@router.post("/checkout")
def checkout(plan: str, user: User = get_current_user()):
    if plan not in PLANS or plan == "free":
        raise HTTPException(400, "Invalid plan")
    url = create_checkout_session(user.id, plan, user.email)
    if not url:
        raise HTTPException(400, "Could not create checkout session")
    return {"url": url}


@router.post("/portal")
def portal(user: User = get_current_user()):
    db = next(get_db())
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(400, "No active subscription")
    url = create_portal_session(user.id, sub.stripe_customer_id)
    if not url:
        raise HTTPException(400, "Could not create portal session")
    return {"url": url}


@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")
    db = next(get_db())
    try:
        result = handle_webhook(payload, sig, db)
        return result
    finally:
        db.close()
