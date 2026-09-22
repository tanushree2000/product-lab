# Payment Dispute Management System

A full-stack portfolio MVP for managing and analyzing payment disputes.

## Stack
- Next.js 16 App Router + React 19 + TypeScript
- Tailwind CSS 4
- FastAPI + Python 3.12
- SQLAlchemy 2 + PostgreSQL 17
- Pydantic 2
- Docker Compose
- Pytest
- Optional OpenAI-generated analyst summaries (the core decision engine works without an API key)

## Features
- Operations dashboard with dispute KPIs
- Searchable dispute queue
- Case detail view
- Evidence completeness tracking
- Explainable recommendation engine
- Human-review routing
- Case status updates
- Audit events
- Seed data
- REST API + OpenAPI docs
- Health check
- Dockerized local setup
- Automated backend tests

> Portfolio/educational software. The sample data is synthetic. The recommendation engine is a transparent demo and must not be used for real financial decisions.

## Fastest way to run

Install Docker Desktop, then:

```bash
cp .env.example .env
docker compose up --build
```

Open:
- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- API health: http://localhost:8000/health

The database is automatically created and seeded.

## Run without Docker

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=sqlite:///./disputes.db
uvicorn app.main:app --reload
```

### Frontend
In another terminal:
```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## GitHub upload

Create an empty GitHub repository named `ai-payment-dispute-management-system`, then run from this folder:

```bash
git init
git add .
git commit -m "Build payment dispute management MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-payment-dispute-management-system.git
git push -u origin main
```

Do not commit `.env` or API keys.

## Product flow
1. Analyst opens dispute queue.
2. Analyst selects a case.
3. API retrieves transaction/evidence data.
4. Explainable engine evaluates evidence completeness.
5. System recommends `CONTEST`, `ACCEPT`, or `HUMAN_REVIEW`.
6. Analyst sees rationale and missing evidence.
7. Analyst updates case status.
8. Audit event is stored.

## API
- `GET /health`
- `GET /api/disputes`
- `GET /api/disputes/{id}`
- `POST /api/disputes`
- `POST /api/disputes/{id}/analyze`
- `PATCH /api/disputes/{id}/status`
- `GET /api/disputes/{id}/events`
- `GET /api/metrics`

## Next portfolio iterations
- Stripe test-mode webhook ingestion
- Evidence document upload to object storage
- RAG over dispute policies with citations
- Authentication / RBAC
- Background jobs
- OpenTelemetry
- Offline evaluation dataset
- Hosted deployment


## Client / portfolio package
- `docs/PRD.md` — product requirements
- `docs/CASE_STUDY.md` — PM case study
- `docs/DEMO_SCRIPT.md` — 5-minute presentation flow
- `docs/RESUME_METRICS.md` — rules for defensible quantified claims
- `evaluation/user-study-template.csv` — collect real task-time data
- `/api/evaluation` — reproducible 100-case synthetic benchmark

## Important metric language
The built-in benchmark is intentionally synthetic. Report it as **agreement on 100 labeled synthetic scenarios**, not "production accuracy." Time-saved and business-impact claims require a real usability/pilot study.
