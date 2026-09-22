from app.evaluation import run_benchmark
def test_benchmark():
    r=run_benchmark()
    assert r["benchmark_cases"] == 100
    assert 0 <= r["agreement_rate"] <= 100
