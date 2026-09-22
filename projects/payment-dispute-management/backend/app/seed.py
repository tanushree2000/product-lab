from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Dispute

SEED = [
    dict(customer="Ava Patel", merchant="Northstar Electronics", amount=899.00, reason="Customer does not recognize transaction",
         transaction_age_days=12, has_receipt=True, has_delivery_proof=True, customer_contacted=True, prior_successful_transactions=3),
    dict(customer="Noah Williams", merchant="Urban Threads", amount=124.50, reason="Item not received",
         transaction_age_days=22, has_receipt=True, has_delivery_proof=False, customer_contacted=True, prior_successful_transactions=1),
    dict(customer="Mia Chen", merchant="CloudBox Software", amount=49.00, reason="Subscription canceled",
         transaction_age_days=41, has_receipt=False, has_delivery_proof=False, customer_contacted=False, prior_successful_transactions=0),
    dict(customer="Ethan Brown", merchant="Atlas Travel", amount=642.80, reason="Service not provided",
         transaction_age_days=18, has_receipt=True, has_delivery_proof=True, customer_contacted=False, prior_successful_transactions=2),
    dict(customer="Sofia Garcia", merchant="Fresh Market", amount=76.25, reason="Duplicate charge",
         transaction_age_days=7, has_receipt=True, has_delivery_proof=False, customer_contacted=True, prior_successful_transactions=5),
]

def seed(db: Session):
    if db.scalar(select(Dispute.id).limit(1)):
        return
    db.add_all([Dispute(**item) for item in SEED])
    db.commit()
