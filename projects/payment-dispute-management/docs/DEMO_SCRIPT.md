# 5-Minute Client Demo Script

## 1. Problem — 30 sec
"This prototype brings dispute triage into one workspace. The analyst can see the case, evidence completeness, recommendation, rationale, missing evidence, and case status without treating automation as the final decision-maker."

## 2. Dashboard — 45 sec
Show total cases, open cases, human-review count, and open exposure. Explain that all data is synthetic.

## 3. Queue — 45 sec
Search for a merchant and filter cases. Open one strong-evidence case.

## 4. Analysis — 90 sec
Show the recommendation, evidence score, rationale, and missing evidence. Explain why the logic is transparent and why ambiguous cases are routed to human review.

## 5. Workflow — 45 sec
Send a case to review or mark it resolved. Refresh metrics and explain the audit trail/API.

## 6. Evaluation — 30 sec
Open `http://localhost:8000/api/evaluation`. Explain that the benchmark uses 100 labeled synthetic scenarios and measures reproducible agreement, not production accuracy.

## 7. Roadmap — 15 sec
Policy RAG with citations → Stripe sandbox ingestion → evidence upload → RBAC → analyst pilot → production observability.
