from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class DisputeCreate(BaseModel):
    customer: str = Field(min_length=1, max_length=120)
    merchant: str = Field(min_length=1, max_length=160)
    amount: float = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    reason: str
    transaction_age_days: int = Field(default=0, ge=0)
    has_receipt: bool = False
    has_delivery_proof: bool = False
    customer_contacted: bool = False
    prior_successful_transactions: int = Field(default=0, ge=0)

class DisputeRead(DisputeCreate):
    id: int
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StatusUpdate(BaseModel):
    status: Literal["open", "review", "contested", "accepted", "resolved"]

class Decision(BaseModel):
    dispute_id: int
    recommendation: Literal["CONTEST", "ACCEPT", "HUMAN_REVIEW"]
    confidence: int
    evidence_score: int
    missing_evidence: list[str]
    rationale: list[str]
    human_review: bool
    analyst_summary: str

class Metrics(BaseModel):
    total_cases: int
    open_cases: int
    resolved_cases: int
    human_review_cases: int
    open_exposure: float

class AuditEventRead(BaseModel):
    id: int
    dispute_id: int
    event_type: str
    detail: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
