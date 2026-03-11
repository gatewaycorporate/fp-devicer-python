from devicer.benchmarks.metrics import calculate_metrics


def test_calculate_metrics_basic_parity_math():
    scored_pairs = [
        {"score": 90, "sameDevice": True, "isAttractor": False},
        {"score": 60, "sameDevice": True, "isAttractor": True},
        {"score": 70, "sameDevice": False, "isAttractor": True},
        {"score": 10, "sameDevice": False, "isAttractor": False},
    ]

    results = calculate_metrics(scored_pairs, thresholds=[50])
    result = results[0]

    assert result.threshold == 50
    assert result.precision == 2 / 3
    assert result.recall == 1.0
    assert result.far == 0.5
    assert result.frr == 0.0
    assert result.eer == 0.5
    assert result.attr == 1.0


def test_calculate_metrics_default_threshold_count():
    scored_pairs = [{"score": 10, "sameDevice": False, "isAttractor": False}]
    results = calculate_metrics(scored_pairs)
    assert len(results) == 21
    assert results[0].threshold == 0
    assert results[-1].threshold == 100
