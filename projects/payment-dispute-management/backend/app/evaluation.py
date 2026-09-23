from app.main import guard, AIOut
def run():
    passed=0
    for i in range(100):
        rule=["CONTEST","ACCEPT","HUMAN_REVIEW"][i%3]; action=rule; conf=.9; risks=[]; expected=rule
        if i%5==0: conf=.6; expected="HUMAN_REVIEW"
        elif i%7==0: action="ACCEPT" if rule=="CONTEST" else "CONTEST"; expected="HUMAN_REVIEW"
        elif i%11==0: risks=["Synthetic risk"]; expected="HUMAN_REVIEW"
        ai=AIOut(summary="",evidence_strengths=[],missing_evidence=[],risk_signals=risks,proposed_action=action,confidence=conf,rationale="")
        actual,_=guard(ai,rule,risks); passed+=actual==expected
    print(f"Synthetic guardrail regression: {passed}/100 expected routes matched.")
    print("Regression coverage only; not real-world model accuracy.")
if __name__=="__main__": run()
