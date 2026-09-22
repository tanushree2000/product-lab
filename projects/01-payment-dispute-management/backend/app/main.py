from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, SessionLocal, engine, get_db
from .models import AuditEvent, Dispute
from .schemas import AuditEventRead, Decision, DisputeCreate, DisputeRead, Metrics, StatusUpdate
from .seed import seed
from .services import analyze_dispute
from .evaluation import run_benchmark

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        seed(db)
    yield

app = FastAPI(
    title="AI Payment Dispute Management System API",
    version="1.0.0",
    description="Portfolio MVP using synthetic data. Not for real financial decisions.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/disputes", response_model=list[DisputeRead])
def list_disputes(
    q: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Dispute).order_by(Dispute.created_at.desc())
    if q:
        term = f"%{q}%"
        stmt = stmt.where(or_(Dispute.customer.ilike(term), Dispute.merchant.ilike(term), Dispute.reason.ilike(term)))
    if status and status != "all":
        stmt = stmt.where(Dispute.status == status)
    return db.scalars(stmt).all()

@app.post("/api/disputes", response_model=DisputeRead, status_code=201)
def create_dispute(payload: DisputeCreate, db: Session = Depends(get_db)):
    dispute = Dispute(**payload.model_dump())
    db.add(dispute)
    db.commit()
    db.refresh(dispute)
    db.add(AuditEvent(dispute_id=dispute.id, event_type="created", detail="Dispute created"))
    db.commit()
    return dispute

@app.get("/api/disputes/{dispute_id}", response_model=DisputeRead)
def get_dispute(dispute_id: int, db: Session = Depends(get_db)):
    dispute = db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(404, "Dispute not found")
    return dispute

@app.post("/api/disputes/{dispute_id}/analyze", response_model=Decision)
def analyze(dispute_id: int, db: Session = Depends(get_db)):
    dispute = db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(404, "Dispute not found")
    result = analyze_dispute(dispute)
    db.add(AuditEvent(dispute_id=dispute.id, event_type="analysis", detail=f"{result.recommendation}; score={result.evidence_score}"))
    db.commit()
    return result

@app.patch("/api/disputes/{dispute_id}/status", response_model=DisputeRead)
def update_status(dispute_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    dispute = db.get(Dispute, dispute_id)
    if not dispute:
        raise HTTPException(404, "Dispute not found")
    previous = dispute.status
    dispute.status = payload.status
    db.add(AuditEvent(dispute_id=dispute.id, event_type="status_changed", detail=f"{previous} -> {payload.status}"))
    db.commit()
    db.refresh(dispute)
    return dispute

@app.get("/api/disputes/{dispute_id}/events", response_model=list[AuditEventRead])
def events(dispute_id: int, db: Session = Depends(get_db)):
    if not db.get(Dispute, dispute_id):
        raise HTTPException(404, "Dispute not found")
    return db.scalars(select(AuditEvent).where(AuditEvent.dispute_id == dispute_id).order_by(AuditEvent.created_at.desc())).all()

@app.get("/api/metrics", response_model=Metrics)
def metrics(db: Session = Depends(get_db)):
    items = db.scalars(select(Dispute)).all()
    analyses = [analyze_dispute(x) for x in items]
    return Metrics(
        total_cases=len(items),
        open_cases=sum(x.status != "resolved" for x in items),
        resolved_cases=sum(x.status == "resolved" for x in items),
        human_review_cases=sum(x.human_review for x in analyses),
        open_exposure=round(sum(x.amount for x in items if x.status != "resolved"), 2),
    )


@app.get("/api/evaluation")
def evaluation():
    return run_benchmark()
