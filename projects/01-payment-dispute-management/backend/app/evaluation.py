from dataclasses import dataclass
from .models import Dispute
from .services import analyze_dispute

@dataclass
class EvalCase:
    dispute: Dispute
    expected: str

def benchmark_cases():
    cases=[]
    # Strong merchant evidence -> contest
    for i in range(40):
        cases.append(EvalCase(Dispute(
            id=1000+i, customer="Synthetic", merchant="Demo Merchant", amount=50+i,
            reason="Item not received", transaction_age_days=10,
            has_receipt=True, has_delivery_proof=True, customer_contacted=True,
            prior_successful_transactions=3), "CONTEST"))
    # Weak evidence + unauthorized claim -> accept
    for i in range(35):
        cases.append(EvalCase(Dispute(
            id=1100+i, customer="Synthetic", merchant="Demo Merchant", amount=80+i,
            reason="Unauthorized transaction", transaction_age_days=60,
            has_receipt=False, has_delivery_proof=False, customer_contacted=False,
            prior_successful_transactions=0), "ACCEPT"))
    # Ambiguous -> human review
    for i in range(25):
        cases.append(EvalCase(Dispute(
            id=1200+i, customer="Synthetic", merchant="Demo Merchant", amount=120+i,
            reason="Service quality dispute", transaction_age_days=20,
            has_receipt=True, has_delivery_proof=False, customer_contacted=True,
            prior_successful_transactions=0), "HUMAN_REVIEW"))
    return cases

def run_benchmark():
    cases=benchmark_cases()
    results=[(c.expected, analyze_dispute(c.dispute).recommendation) for c in cases]
    correct=sum(a==b for a,b in results)
    return {
        "benchmark_cases": len(cases),
        "agreement_rate": round(correct/len(cases)*100,1),
        "correct": correct,
        "human_review_cases": sum(pred=="HUMAN_REVIEW" for _,pred in results),
        "methodology": "100 deterministic synthetic labeled scenarios across strong-evidence, weak-evidence, and ambiguous cohorts."
    }
