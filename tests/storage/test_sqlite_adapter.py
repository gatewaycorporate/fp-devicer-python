import uuid
from datetime import UTC, datetime, timedelta

import pytest

from devicer.libs.adapters import create_sqlite_adapter
from devicer.types import StoredFingerprint
from tests.fixtures.fingerprints import fp_identical, fp_very_similar


@pytest.mark.asyncio
async def test_sqlite_adapter_crud_and_candidates(tmp_path):
    adapter = create_sqlite_adapter(str(tmp_path / "test-db.sqlite"))
    await adapter.init()

    await adapter.delete_old_snapshots(0)

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

    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_b", timestamp=datetime.now(UTC), fingerprint=fp_very_similar))
    candidates = await adapter.find_candidates(fp_identical, 70, 5)
    assert len(candidates) >= 1
    assert candidates[0].confidence >= 70

    old_date = datetime.now(UTC) - timedelta(days=31)
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="old_dev", timestamp=old_date, fingerprint=fp_identical))
    deleted = await adapter.delete_old_snapshots(30)
    assert deleted >= 1

    all_entries = await adapter.get_all_fingerprints()
    assert len(all_entries) >= 2
    await adapter.close()
