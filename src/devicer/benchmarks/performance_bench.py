from __future__ import annotations

import asyncio
from datetime import datetime, UTC
from pathlib import Path
from time import perf_counter
from typing import Dict

from ..core.manager import DeviceManager
from ..libs.adapters.inmemory import create_in_memory_adapter
from ..libs.adapters.sqlite import create_sqlite_adapter
from ..libs.confidence import calculate_confidence
from .data_generator import generate_dataset


async def _measure_batch_confidence(base: Dict, mutated: Dict, iterations: int) -> float:
    start = perf_counter()
    for _ in range(iterations):
        calculate_confidence(base, mutated)
    end = perf_counter()
    return (end - start) * 1000 / iterations


async def _measure_batch_identify(manager: DeviceManager, data: Dict, iterations: int) -> float:
    start = perf_counter()
    for i in range(iterations):
        await manager.identify(data, user_id=f"benchmark_{i}")
    end = perf_counter()
    return (end - start) * 1000 / iterations


async def run_performance_benchmark(
    dataset_size: int = 50,
    confidence_iterations: int = 1000,
    identify_iterations: int = 50,
    sqlite_file_path: str | None = None,
) -> str:
    dataset = generate_dataset(dataset_size)
    base = dataset[0].data
    mutated = dataset[5].data

    in_memory_adapter = create_in_memory_adapter()
    sqlite_memory_adapter = create_sqlite_adapter(":memory:")

    default_sqlite_file = Path(__file__).with_name("benchmark-sqlite.db")
    sqlite_disk_path = sqlite_file_path or str(default_sqlite_file)
    sqlite_file_adapter = create_sqlite_adapter(sqlite_disk_path)

    await sqlite_memory_adapter.init()
    await sqlite_file_adapter.init()

    in_memory_manager = DeviceManager(in_memory_adapter)
    sqlite_memory_manager = DeviceManager(sqlite_memory_adapter)
    sqlite_file_manager = DeviceManager(sqlite_file_adapter)

    confidence_time = await _measure_batch_confidence(base, mutated, confidence_iterations)
    in_memory_time = await _measure_batch_identify(in_memory_manager, base, identify_iterations)
    sqlite_memory_time = await _measure_batch_identify(sqlite_memory_manager, base, identify_iterations)
    sqlite_file_time = await _measure_batch_identify(sqlite_file_manager, base, identify_iterations)

    output = "\n".join(
        [
            f"--- Performance Metrics ({datetime.now(UTC).isoformat()}) ---",
            f"calculateConfidence (hybrid scorer): {confidence_time:.2f} ms (per call)",
            f"DeviceManager.identify (In-Memory): {in_memory_time:.2f} ms ({(in_memory_time / confidence_time):.2f}x longer than confidence)",
            f"DeviceManager.identify (SQLite in-memory): {sqlite_memory_time:.2f} ms ({(sqlite_memory_time / confidence_time):.2f}x longer than confidence)",
            f"DeviceManager.identify (SQLite file-based): {sqlite_file_time:.2f} ms ({(sqlite_file_time / confidence_time):.2f}x longer than confidence)",
        ]
    )

    out_path = Path(__file__).with_name("performance.bench.out")
    out_path.write_text(output, encoding="utf-8")

    await sqlite_memory_adapter.close()
    await sqlite_file_adapter.close()

    return output


def main() -> None:
    print(asyncio.run(run_performance_benchmark()))


if __name__ == "__main__":
    main()
