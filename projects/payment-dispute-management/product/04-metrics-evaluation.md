# Metrics and evaluation

## Product metrics for real validation
- median analyst time per case
- evidence-gap precision/recall
- analyst agreement with recommendations
- human-review rate
- recommendation override rate
- analyst confidence/trust
- cost per analyzed case

## AI quality
Groundedness, structured-output validity, action agreement on expert labels, confidence calibration, missing-evidence quality, and high-risk routing recall.

## Current benchmark
A 100-case synthetic guardrail regression suite tests low-confidence, disagreement, and risk routing. It is not production model accuracy.

## Validation plan
Expert-labeled scenarios → 3–5 moderated workflow tests → baseline vs assisted task time → disagreement/override analysis → iteration.
