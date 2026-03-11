# FP-Devicer

## Developed by Gateway Corporate Solutions LLC

FP-Devicer is a digital fingerprinting middleware library designed for ease of
use and near-universal compatibility with servers.

### Usage

Importing and using the library to compare fingerprints between users is as
simple as collecting user data and running a confidence calculation.

```python
# 1. Simple method (using defaults)
from devicer import calculate_confidence

score = calculate_confidence(fp_data_1, fp_data_2)

# 2. Advanced method (custom weights & comparators)
from devicer import ComparisonOptions, create_confidence_calculator, register_plugin
from devicer.libs.comparators import levenshtein_similarity

register_plugin(
  "userAgent",
  weight=25,
  comparator=lambda a, b, _path=None: levenshtein_similarity(
    str(a or "").lower(),
    str(b or "").lower(),
  ),
)

advanced_calculator = create_confidence_calculator(
  ComparisonOptions(
    weights={
      "platform": 20,
      "fonts": 20,
      "screen": 15,
    },
  )
)

advanced_score = advanced_calculator.calculate_confidence(fp_data_1, fp_data_2)
```

For storage-backed identification flows:

```python
import asyncio
from devicer import DeviceManager, create_in_memory_adapter


async def main() -> None:
  adapter = create_in_memory_adapter()
  await adapter.init()
  manager = DeviceManager(adapter)

  result = await manager.identify(
    {
      "userAgent": "Mozilla/5.0",
      "platform": "Linux x86_64",
      "languages": ["en-US", "en"],
    },
    user_id="user-1",
    ip="127.0.0.1",
  )
  print(result)  # -> IdentifyResult(device_id=..., confidence=..., is_new_device=...)


asyncio.run(main())
```

The resulting confidence ranges between 0 and 100, where 100 is the strongest
match.

### Quickstart

Install and run the Python package:

```sh
pip install devicer.py
python -c "from devicer import calculate_confidence; print(calculate_confidence({'platform':'Win32'},{'platform':'Win32'}))"
```

For local development:

```sh
pip install -e .[dev]
pytest -q
```

### Adapters

Built-in adapters:

- `create_in_memory_adapter()`
- `create_sqlite_adapter(path)`
- `create_postgres_adapter(dsn)` _(requires optional `postgres` extras)_
- `create_redis_adapter(url)` _(requires optional `redis` extras)_

Install optional adapter dependencies:

```sh
pip install -e .[postgres]
pip install -e .[redis]
```

### Benchmarks

You can run benchmark parity scripts for performance and accuracy:

```sh
python -m devicer.benchmarks.performance_bench
python -m devicer.benchmarks.accuracy_bench
```

Outputs are written to:

- `src/devicer/benchmarks/performance.bench.out`
- `src/devicer/benchmarks/accuracy.bench.out`

### Documentation

The TypeScript SDK documentation is available at
[gatewaycorporate.github.io/fp-devicer](https://gatewaycorporate.github.io/fp-devicer/).
The Python package mirrors the same core architecture (`core`, `libs`,
`benchmarks`, and `types`) with Pythonic APIs.

### Whitepaper

The whitepaper covers the theory, architecture, and design decisions behind
FP-Devicer. You can read it
[here](https://gatewaycorporate.org/papers/FP-Devicer.pdf).
