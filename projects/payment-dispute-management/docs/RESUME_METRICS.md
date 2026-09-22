# Resume Metrics — Use Carefully

## Metrics already reproducible from the repository
Run:
`GET /api/evaluation`

The benchmark contains 100 synthetic labeled scenarios. You may accurately describe the result as a **synthetic benchmark agreement rate**, not as real-world accuracy.

## Metrics that require a user study
Do not claim these until measured:
- analyst time saved
- percentage reduction in resolution time
- adoption
- customer satisfaction
- money saved
- production dispute win rate

## Recommended study
Recruit 5–10 testers. Give each 5 cases using a manual baseline and 5 cases using the prototype. Record:
- start/end time
- selected action
- confidence (1–5)
- missing evidence identified
- usability score

Then calculate median task time and error rate. Add the raw anonymized results to `evaluation/user-study.csv`.
