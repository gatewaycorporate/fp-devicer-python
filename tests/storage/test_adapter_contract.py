import uuid
from datetime import UTC, datetime

import pytest

from devicer import StoredFingerprint, create_in_memory_adapter
from tests.fixtures.fingerprints import fp_identical, fp_very_different, fp_very_similar


@pytest.mark.asyncio
async def test_inmemory_storage_adapter_contract():
    adapter = create_in_memory_adapter()
    await adapter.init()
    await adapter.init()

    assert await adapter.find_candidates(fp_identical, 0, 10) == []

    device_id = f"dev_contract_{uuid.uuid4()}"
    snapshot = StoredFingerprint(
        id=str(uuid.uuid4()),
        device_id=device_id,
        timestamp=datetime.now(UTC),
        fingerprint=fp_identical,
    )
    await adapter.save(snapshot)

    await adapter.link_to_user(device_id, "user_contract_123")
    assert await adapter.get_history("dev_nonexistent", 10) == []

    history = await adapter.get_history(device_id, 5)
    assert len(history) == 1
    assert history[0].id == snapshot.id

    await adapter.save(StoredFingerprint(
        id=str(uuid.uuid4()),
        device_id=f"dev_other_{uuid.uuid4()}",
        timestamp=datetime.now(UTC),
        fingerprint=fp_very_similar,
    ))
    await adapter.save(StoredFingerprint(
        id=str(uuid.uuid4()),
        device_id=f"dev_diff_{uuid.uuid4()}",
        timestamp=datetime.now(UTC),
        fingerprint=fp_very_different,
    ))

    candidates = await adapter.find_candidates(fp_identical, 90, 10)
    assert all(candidate.confidence >= 90 for candidate in candidates)

    all_snapshots = await adapter.get_all_fingerprints()
    assert len(all_snapshots) >= 3
