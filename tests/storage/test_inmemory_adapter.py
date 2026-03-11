import uuid
from datetime import UTC, datetime

import pytest

from devicer.libs.adapters import create_in_memory_adapter
from devicer.types import StoredFingerprint
from tests.fixtures.fingerprints import fp_identical, fp_very_similar


@pytest.mark.asyncio
async def test_inmemory_save_and_history():
    adapter = create_in_memory_adapter()
    device_id = "dev_test_001"
    snapshot = StoredFingerprint(
        id=str(uuid.uuid4()),
        device_id=device_id,
        timestamp=datetime.now(UTC),
        fingerprint=fp_identical,
        user_id="user_123",
    )

    await adapter.save(snapshot)
    history = await adapter.get_history(device_id, 10)

    assert len(history) == 1
    assert history[0].device_id == device_id
    assert history[0].user_id == "user_123"


@pytest.mark.asyncio
async def test_inmemory_find_candidates_sorted():
    adapter = create_in_memory_adapter()
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_a", timestamp=datetime.now(UTC), fingerprint=fp_identical))
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_b", timestamp=datetime.now(UTC), fingerprint=fp_very_similar))

    candidates = await adapter.find_candidates(fp_identical, 70, 5)
    assert len(candidates) > 0
    assert candidates[0].device_id == "dev_a"
    assert candidates[0].confidence >= 90
    for i in range(1, len(candidates)):
        assert candidates[i].confidence <= candidates[i - 1].confidence


@pytest.mark.asyncio
async def test_inmemory_delete_old_snapshots_and_get_all():
    adapter = create_in_memory_adapter()
    count = await adapter.delete_old_snapshots(30)
    assert count >= 0

    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_a", timestamp=datetime.now(UTC), fingerprint=fp_identical))
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_b", timestamp=datetime.now(UTC), fingerprint=fp_very_similar))

    all_fingerprints = await adapter.get_all_fingerprints()
    assert len(all_fingerprints) == 2
