import os, json
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Float, Integer, Boolean, DateTime, Text, or_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session

DB=os.getenv("DATABASE_URL","sqlite:///./disputes.db")
engine=create_engine(DB,pool_pre_ping=True,connect_args={"check_same_thread":False} if DB.startswith("sqlite") else {})
Local=sessionmaker(bind=engine)
class Base(DeclarativeBase): pass

class Dispute(Base):
    __tablename__="disputes"
    id:Mapped[int]=mapped_column(primary_key=True)
    customer:Mapped[str]=mapped_column(String(120)); merchant:Mapped[str]=mapped_column(String(160))
    amount:Mapped[float]=mapped_column(Float); reason:Mapped[str]=mapped_column(String(200))
    status:Mapped[str]=mapped_column(String(40),default="OPEN"); days_old:Mapped[int]=mapped_column(Integer,default=5)
    receipt:Mapped[bool]=mapped_column(Boolean,default=False); delivery_proof:Mapped[bool]=mapped_column(Boolean,default=False)
    customer_contacted:Mapped[bool]=mapped_column(Boolean,default=False); prior_successful:Mapped[int]=mapped_column(Integer,default=0)
    device_evidence:Mapped[bool]=mapped_column(Boolean,default=False); notes:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class Analysis(Base):
    __tablename__="analyses"
    id:Mapped[int]=mapped_column(primary_key=True); dispute_id:Mapped[int]=mapped_column(Integer,index=True)
    provider:Mapped[str]=mapped_column(String(40)); model:Mapped[str]=mapped_column(String(80))
    summary:Mapped[str]=mapped_column(Text); strengths:Mapped[str]=mapped_column(Text); missing:Mapped[str]=mapped_column(Text)
    risks:Mapped[str]=mapped_column(Text); ai_action:Mapped[str]=mapped_column(String(40)); confidence:Mapped[float]=mapped_column(Float)
    rule_action:Mapped[str]=mapped_column(String(40)); score:Mapped[int]=mapped_column(Integer)
    final_route:Mapped[str]=mapped_column(String(40)); rationale:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class Event(Base):
    __tablename__="events"
    id:Mapped[int]=mapped_column(primary_key=True); dispute_id:Mapped[int]=mapped_column(Integer,index=True)
    kind:Mapped[str]=mapped_column(String(60)); detail:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class StatusBody(BaseModel): status:str
class AIOut(BaseModel):
    summary:str; evidence_strengths:list[str]; missing_evidence:list[str]; risk_signals:list[str]
    proposed_action:str; confidence:float=Field(ge=0,le=1); rationale:str

def dbdep():
    db=Local()
    try: yield db
    finally: db.close()

def rules(d):
    s=0; good=[]; missing=[]; risk=[]
    for yes,pts,label in [(d.receipt,25,"Receipt / transaction record"),(d.delivery_proof,30,"Delivery / service proof"),(d.customer_contacted,15,"Customer communication")]:
        if yes: s+=pts; good.append(label)
        else: missing.append(label)
    if d.prior_successful>=2: s+=20; good.append("Prior successful transaction history")
    else: missing.append("Stronger transaction history")
    if d.days_old<=30: s+=10; good.append("Recent dispute")
    r=d.reason.lower()
    if any(x in r for x in ["fraud","unauthorized","not recognize","does not recognize"]):
        s-=10; risk.append("Authorization / fraud allegation")
        if d.device_evidence: good.append("Device / authorization evidence")
        else: missing.append("Device / authorization evidence")
    s=max(0,min(100,s))
    action="CONTEST" if s>=70 else "ACCEPT" if s<=35 else "HUMAN_REVIEW"
    return s,action,good,list(dict.fromkeys(missing)),risk

def fallback(d):
    s,a,g,m,r=rules(d)
    return AIOut(summary=f"{d.customer} disputes a ${d.amount:.2f} transaction with {d.merchant} for '{d.reason}'.",
        evidence_strengths=g,missing_evidence=m,risk_signals=r,proposed_action=a,
        confidence=.86 if a!="HUMAN_REVIEW" else .64,
        rationale=f"Fallback analyst assessed explicit case evidence at {s}/100."),"fallback","deterministic-v1"

def ai_analyze(d):
    key=os.getenv("OPENAI_API_KEY","").strip(); model=os.getenv("OPENAI_MODEL","gpt-5.6-luna")
    if not key: return fallback(d)
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        payload={k:getattr(d,k) for k in ["customer","merchant","amount","reason","days_old","receipt","delivery_proof","customer_contacted","prior_successful","device_evidence","notes"]}
        instructions="""You assist payment-dispute analysts. Use only supplied evidence; never invent facts.
Return ONLY valid JSON with keys summary, evidence_strengths, missing_evidence, risk_signals, proposed_action, confidence, rationale.
proposed_action must be CONTEST, ACCEPT, or HUMAN_REVIEW. confidence is 0 to 1. Prefer HUMAN_REVIEW for ambiguity/high risk. A human makes the final decision."""
        res=client.responses.create(model=model,instructions=instructions,input=json.dumps(payload))
        text=res.output_text.strip()
        if text.startswith("```"):
            text=text.replace("```json","").replace("```","").strip()
        return AIOut.model_validate(json.loads(text)),"openai",model
    except Exception:
        return fallback(d)

def guard(ai,rule,risks):
    if ai.confidence<.72: return "HUMAN_REVIEW","AI confidence below routing threshold."
    if ai.proposed_action!=rule: return "HUMAN_REVIEW","AI and deterministic guardrail disagree."
    if risks and ai.proposed_action!="HUMAN_REVIEW": return "HUMAN_REVIEW","Risk signal requires analyst review."
    return ai.proposed_action,"AI recommendation passed deterministic guardrails."

def dd(d): return {k:getattr(d,k) for k in ["id","customer","merchant","amount","reason","status","days_old","receipt","delivery_proof","customer_contacted","prior_successful","device_evidence","notes"]}
def ad(a): return {"provider":a.provider,"model":a.model,"summary":a.summary,"evidence_strengths":json.loads(a.strengths),"missing_evidence":json.loads(a.missing),"risk_signals":json.loads(a.risks),"ai_action":a.ai_action,"ai_confidence":a.confidence,"rule_action":a.rule_action,"evidence_score":a.score,"final_route":a.final_route,"rationale":a.rationale}

app=FastAPI(title="Payment Dispute Management API",version="2.0")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in os.getenv("CORS_ORIGINS","http://localhost:3000").split(",")],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

SEED=[
("Ava Patel","Northstar Electronics",899,"Customer does not recognize transaction",8,1,0,1,3,0,"Customer reported the transaction after reviewing the monthly statement."),
("Noah Williams","Urban Threads",124.5,"Item not received",12,1,0,1,0,0,"Order confirmation exists but no carrier delivery scan."),
("Mia Chen","CloudBox Software",49,"Subscription canceled",21,1,1,1,5,1,"Merchant records show service access continued after the disputed billing date."),
("Ethan Brown","Atlas Travel",642.8,"Service not provided",38,1,0,0,1,0,"Travel booking exists; fulfillment evidence is incomplete."),
("Sofia Garcia","Fresh Market",76.25,"Duplicate charge",6,1,0,1,4,0,"Two similar amounts appear within minutes; receipt covers one purchase.")
]
@app.on_event("startup")
def start():
    Base.metadata.create_all(engine); db=Local()
    if db.query(Dispute).count()==0:
        for x in SEED:
            db.add(Dispute(customer=x[0],merchant=x[1],amount=x[2],reason=x[3],days_old=x[4],receipt=bool(x[5]),delivery_proof=bool(x[6]),customer_contacted=bool(x[7]),prior_successful=x[8],device_evidence=bool(x[9]),notes=x[10]))
        db.commit()
    db.close()

@app.get("/health")
def health(): return {"status":"ok"}

@app.get("/api/disputes")
def list_cases(db:Session=Depends(dbdep)): return [dd(x) for x in db.query(Dispute).order_by(Dispute.id.desc()).all()]

@app.get("/api/disputes/{id}")
def get_case(id:int,db:Session=Depends(dbdep)):
    d=db.get(Dispute,id)
    if not d: raise HTTPException(404)
    a=db.query(Analysis).filter(Analysis.dispute_id==id).order_by(Analysis.id.desc()).first()
    return {"case":dd(d),"analysis":ad(a) if a else None}

@app.post("/api/disputes/{id}/analyze")
def analyze(id:int,db:Session=Depends(dbdep)):
    d=db.get(Dispute,id)
    if not d: raise HTTPException(404)
    ai,provider,model=ai_analyze(d); score,ra,_,_,rr=rules(d)
    route,why=guard(ai,ra,list(dict.fromkeys(ai.risk_signals+rr)))
    a=Analysis(dispute_id=id,provider=provider,model=model,summary=ai.summary,strengths=json.dumps(ai.evidence_strengths),missing=json.dumps(ai.missing_evidence),risks=json.dumps(ai.risk_signals),ai_action=ai.proposed_action,confidence=ai.confidence,rule_action=ra,score=score,final_route=route,rationale=f"{ai.rationale} Guardrail: {why}")
    if route=="HUMAN_REVIEW": d.status="REVIEW"
    db.add(a); db.add(Event(dispute_id=id,kind="AI_ANALYSIS",detail=f"{provider}/{model}: {route}")); db.commit(); db.refresh(a)
    return ad(a)

@app.patch("/api/disputes/{id}/status")
def status(id:int,body:StatusBody,db:Session=Depends(dbdep)):
    if body.status not in {"OPEN","REVIEW","CONTESTED","ACCEPTED","ESCALATED","CLOSED"}: raise HTTPException(400,"Invalid status")
    d=db.get(Dispute,id)
    if not d: raise HTTPException(404)
    old=d.status; d.status=body.status; db.add(Event(dispute_id=id,kind="ANALYST_DECISION",detail=f"{old} → {body.status}")); db.commit()
    return dd(d)

@app.get("/api/disputes/{id}/events")
def events(id:int,db:Session=Depends(dbdep)):
    return [{"kind":x.kind,"detail":x.detail,"created_at":x.created_at.isoformat()} for x in db.query(Event).filter(Event.dispute_id==id).order_by(Event.id.desc()).all()]

@app.get("/api/metrics")
def metrics(db:Session=Depends(dbdep)):
    rows=db.query(Dispute).all(); openrows=[x for x in rows if x.status not in {"CLOSED","ACCEPTED","CONTESTED"}]
    return {"open_cases":len(openrows),"open_exposure":round(sum(x.amount for x in openrows),2),"human_review":sum(x.status=="REVIEW" for x in rows),"analyses_run":db.query(Analysis).count()}
