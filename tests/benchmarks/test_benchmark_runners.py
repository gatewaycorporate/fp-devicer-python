from pathlib import Path

import pytest

from devicer.benchmarks.accuracy_bench import run_accuracy_benchmark
from devicer.benchmarks.performance_bench import run_performance_benchmark


def test_run_accuracy_benchmark_writes_output_file():
    payload = run_accuracy_benchmark(dataset_size=60, sessions_per_device=3)
    out_path = Path(__file__).resolve().parents[2] / "src" / "devicer" / "benchmarks" / "accuracy.bench.out"

    assert out_path.exists()
    assert "Accuracy Metrics" in payload["output"]
    assert payload["best"].threshold >= 0


@pytest.mark.asyncio
async def test_run_performance_benchmark_writes_output_file(tmp_path):
    sqlite_path = tmp_path / "perf.db"
    output = await run_performance_benchmark(
        dataset_size=20,
        confidence_iterations=20,
        identify_iterations=5,
        sqlite_file_path=str(sqlite_path),
    )
    out_path = Path(__file__).resolve().parents[2] / "src" / "devicer" / "benchmarks" / "performance.bench.out"

    assert out_path.exists()
    assert "Performance Metrics" in output
    assert "calculateConfidence" in output
