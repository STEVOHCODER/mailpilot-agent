import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime,
    ForeignKey, JSON, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, default="")
    password_hash = Column(String(255), nullable=False)
    timezone = Column(String(50), default="UTC")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    subscription = relationship("Subscription", back_populates="user", uselist=False)
    email_connections = relationship("EmailConnection", back_populates="user")
    whatsapp_connection = relationship("WhatsAppConnection", back_populates="user", uselist=False)
    forwarding_rules = relationship("ForwardingRule", back_populates="user")
    message_logs = relationship("MessageLog", back_populates="user")
    usage = relationship("Usage", back_populates="user", uselist=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    plan = Column(String(50), default="free")  # free, starter, pro, business
    status = Column(String(50), default="active")  # active, cancelled, past_due, trial
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_customer_id = Column(String(255), nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="subscription")


class EmailConnection(Base):
    __tablename__ = "email_connections"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # gmail, outlook, imap
    email_address = Column(String(255), nullable=False)
    encrypted_token = Column(Text, nullable=True)  # OAuth token or app password (encrypted)
    token_refresh = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    imap_host = Column(String(255), nullable=True)
    imap_port = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="email_connections")


class WhatsAppConnection(Base):
    __tablename__ = "whatsapp_connections"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    phone_number = Column(String(50), nullable=False)
    meta_phone_number_id = Column(String(255), nullable=False)
    meta_access_token = Column(Text, nullable=False)  # Encrypted
    is_active = Column(Boolean, default=True)
    last_message_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="whatsapp_connection")


class ForwardingRule(Base):
    __tablename__ = "forwarding_rules"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, default="Default Rule")
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # Conditions (JSON)
    sender_emails = Column(JSON, default=list)  # ["boss@company.com"]
    sender_domains = Column(JSON, default=list)  # ["company.com"]
    subject_contains = Column(JSON, default=list)  # ["urgent", "invoice"]
    body_contains = Column(JSON, default=list)
    has_attachments = Column(Boolean, nullable=True)  # None = any, True = must have, False = none
    min_importance_score = Column(Integer, default=0)

    # Actions
    forward_to_whatsapp = Column(Boolean, default=True)
    summarize_with_ai = Column(Boolean, default=True)
    custom_message_template = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="forwarding_rules")


class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    email_connection_id = Column(String, ForeignKey("email_connections.id"), nullable=True)
    email_message_id = Column(String(500), nullable=True)  # Original email Message-ID
    email_subject = Column(String(500), nullable=True)
    email_sender = Column(String(255), nullable=True)
    email_received_at = Column(DateTime, nullable=True)
    classification_score = Column(Float, default=0)
    classification_reason = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    forwarded = Column(Boolean, default=False)
    whatsapp_message_id = Column(String(255), nullable=True)
    delivery_status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    delivery_error = Column(Text, nullable=True)
    rule_id = Column(String, ForeignKey("forwarding_rules.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    user = relationship("User", back_populates="message_logs")


class Usage(Base):
    __tablename__ = "usage"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    emails_received = Column(Integer, default=0)
    emails_processed = Column(Integer, default=0)
    messages_forwarded = Column(Integer, default=0)
    messages_failed = Column(Integer, default=0)
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="usage")
