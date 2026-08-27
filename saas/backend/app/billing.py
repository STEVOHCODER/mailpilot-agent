"""Stripe billing integration."""
import os
import stripe
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import User, Subscription

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PLANS = {
    "free": {"price_id": None, "messages_day": 25, "price_month": 0},
    "pro": {"price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""), "messages_day": 250, "price_month": 10},
    "enterprise": {"price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""), "messages_day": -1, "price_month": 49},
}


def create_checkout_session(user_id: str, plan: str, email: str) -> str | None:
    price_id = PLANS.get(plan, {}).get("price_id")
    if not price_id:
        return None
    session = stripe.checkout.Session.create(
        mode="subscription",
        payment_method_types=["card"],
        line_items=[{"price": price_id, "quantity": 1}],
        customer_email=email,
        metadata={"user_id": user_id, "plan": plan},
        success_url=os.getenv("FRONTEND_URL", "http://localhost:5173") + "/dashboard?upgraded=true",
        cancel_url=os.getenv("FRONTEND_URL", "http://localhost:5173") + "/dashboard?upgrade=cancelled",
    )
    return session.url


def create_portal_session(user_id: str, stripe_customer_id: str) -> str | None:
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=os.getenv("FRONTEND_URL", "http://localhost:5173") + "/dashboard",
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str, db: Session) -> dict:
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except (stripe.error.SignatureVerificationError, ValueError):
        return {"error": "Invalid signature"}

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"]["user_id"]
        plan = session["metadata"]["plan"]
        sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        if sub:
            sub.plan = plan
            sub.stripe_customer_id = session.get("customer", "")
            sub.stripe_subscription_id = session.get("subscription", "")
            sub.status = "active"
            sub.updated_at = datetime.now(timezone.utc)
        else:
            sub = Subscription(
                user_id=user_id,
                plan=plan,
                stripe_customer_id=session.get("customer", ""),
                stripe_subscription_id=session.get("subscription", ""),
                status="active",
            )
            db.add(sub)
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.plan = plan
        db.commit()

    elif event["type"] == "customer.subscription.deleted":
        sub_data = event["data"]["object"]
        sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == sub_data["id"]).first()
        if sub:
            sub.plan = "free"
            sub.status = "cancelled"
            sub.updated_at = datetime.now(timezone.utc)
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                user.plan = "free"
            db.commit()

    elif event["type"] == "invoice.payment_failed":
        sub_data = event["data"]["object"]
        sub = db.query(Subscription).filter(Subscription.stripe_customer_id == sub_data["customer"]).first()
        if sub:
            sub.status = "past_due"
            db.commit()

    return {"ok": True}
