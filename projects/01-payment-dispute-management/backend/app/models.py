from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Dispute(Base):
    __tablename__ = "disputes"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(120))
    merchant: Mapped[str] = mapped_column(String(160))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    reason: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="open")
    transaction_age_days: Mapped[int] = mapped_column(Integer, default=0)
    has_receipt: Mapped[bool] = mapped_column(Boolean, default=False)
    has_delivery_proof: Mapped[bool] = mapped_column(Boolean, default=False)
    customer_contacted: Mapped[bool] = mapped_column(Boolean, default=False)
    prior_successful_transactions: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    dispute_id: Mapped[int] = mapped_column(ForeignKey("disputes.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(60))
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
