from .models import Dispute
from .schemas import Decision

def analyze_dispute(d: Dispute) -> Decision:
    score = 0
    rationale: list[str] = []
    missing: list[str] = []

    if d.has_receipt:
        score += 25
        rationale.append("Receipt or order confirmation is available.")
    else:
        missing.append("Receipt or order confirmation")

    if d.has_delivery_proof:
        score += 30
        rationale.append("Delivery or service-fulfillment evidence is available.")
    else:
        missing.append("Delivery or service proof")

    if d.customer_contacted:
        score += 15
        rationale.append("Customer communication is documented.")
    else:
        missing.append("Customer communication")

    if d.prior_successful_transactions >= 2:
        score += 20
        rationale.append("Multiple prior successful transactions support merchant history.")

    if d.transaction_age_days <= 30:
        score += 10
        rationale.append("The transaction is recent, improving evidence availability.")

    reason = d.reason.lower()
    if any(term in reason for term in ("fraud", "unauthorized", "not recognize", "not recognised")):
        score -= 10
        missing.append("Authorization/device evidence")
        rationale.append("Unauthorized-transaction claims require stronger authorization evidence.")

    score = max(0, min(100, score))

    if score >= 70:
        rec = "CONTEST"
        confidence = min(95, 70 + (score - 70))
    elif score <= 35:
        rec = "ACCEPT"
        confidence = min(95, 70 + (35 - score))
    else:
        rec = "HUMAN_REVIEW"
        confidence = 60

    missing = list(dict.fromkeys(missing))
    summary = (
        f"Evidence score {score}/100. Recommended action: {rec.replace('_', ' ').title()}. "
        + ("Collect missing evidence before action." if missing else "Current evidence package is comparatively complete.")
    )
    return Decision(
        dispute_id=d.id,
        recommendation=rec,
        confidence=confidence,
        evidence_score=score,
        missing_evidence=missing,
        rationale=rationale,
        human_review=rec == "HUMAN_REVIEW" or confidence < 70,
        analyst_summary=summary,
    )
