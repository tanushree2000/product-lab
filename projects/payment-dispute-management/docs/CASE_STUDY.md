# Product Case Study

## Hypothesis
A unified dispute workspace with evidence completeness and explainable recommendations can reduce the cognitive and navigation burden of dispute triage.

## Discovery assumptions
Analysts need to answer three questions quickly:
1. What happened?
2. What evidence do we have?
3. What should happen next?

These are product assumptions for the prototype and should be validated with real user interviews before representing them as customer findings.

## MVP decision
The prototype prioritizes triage and decision support over automated dispute submission. This keeps the workflow demonstrable while preserving human oversight.

## Product decisions
- Explainable deterministic decision engine first, rather than hiding logic behind an LLM.
- Human-review state for ambiguous evidence.
- Synthetic data only.
- Audit events for traceability.
- PostgreSQL-backed API so the prototype behaves like a real application.
- Evaluation endpoint so performance claims are reproducible.

## Evaluation
The repository contains 100 labeled synthetic scenarios. Run the benchmark through `/api/evaluation`.

The benchmark measures agreement with the labels encoded in the test design. It is **not** evidence of real-world chargeback accuracy. A client pilot would require policy-specific labels and analyst review.

## Next experiments
1. Run a 5–10 person usability study and measure median triage time.
2. Compare workflow against spreadsheet/manual baseline.
3. Add policy RAG and measure citation correctness.
4. Add analyst override reasons and measure recommendation acceptance.
5. Test Stripe sandbox ingestion.
