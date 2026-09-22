from app.models import Dispute
from app.services import analyze_dispute

def test_strong_evidence_contest():
    d = Dispute(id=1, customer="Test", merchant="Shop", amount=100, reason="Item not received",
                transaction_age_days=5, has_receipt=True, has_delivery_proof=True,
                customer_contacted=True, prior_successful_transactions=3)
    result = analyze_dispute(d)
    assert result.recommendation == "CONTEST"
    assert result.evidence_score >= 70

def test_weak_evidence_accept():
    d = Dispute(id=2, customer="Test", merchant="Shop", amount=100, reason="Unauthorized fraud",
                transaction_age_days=60, has_receipt=False, has_delivery_proof=False,
                customer_contacted=False, prior_successful_transactions=0)
    result = analyze_dispute(d)
    assert result.recommendation == "ACCEPT"
    assert result.evidence_score <= 35
