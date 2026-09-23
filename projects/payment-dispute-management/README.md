# Payment Dispute Management System

A working AI-assisted fintech operations MVP for payment-dispute investigation.

**Workflow:** Queue → Case → AI analysis → deterministic guardrails → analyst decision → audit trail.

The AI analyst produces a case summary, evidence strengths, missing evidence, risk signals, a proposed action, confidence, and rationale. Deterministic rules independently assess objective evidence. Low-confidence, risky, or disagreement cases route to human review. The analyst—not the AI—makes the final financial decision.

## Run
Requires Docker Desktop.

```bash
cp .env.example .env
docker compose up --build
```

Open `http://localhost:3000`. API docs are at `http://localhost:8000/docs`.

The product works without an API key using a deterministic fallback analyst. To use the live LLM path, add `OPENAI_API_KEY` to `.env` and restart. Never commit `.env`.

## MVP
- dispute dashboard and queue
- searchable cases
- AI/fallback case synthesis
- evidence strengths and gaps
- risk signals
- recommendation + confidence
- deterministic evidence guardrails
- AI/rules disagreement detection
- human-review routing
- analyst final decision
- audit trail
- synthetic evaluation suite
- seeded demo data

## Stack
Next.js · TypeScript · Tailwind · FastAPI · Python · PostgreSQL · SQLAlchemy · OpenAI Responses API · Docker

## Evaluation
```bash
docker compose exec backend python -m app.evaluation
```
The 100-case benchmark is synthetic regression coverage. It is not a claim of production model accuracy or business impact.

## PM work
See `product/` for the PRD, problem framing, product decisions, metrics/evaluation plan, and next iterations.

This is a portfolio prototype using synthetic data. It does not claim real customer adoption, realized time savings, production accuracy, or financial impact.
