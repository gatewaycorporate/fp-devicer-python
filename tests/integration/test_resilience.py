import pytest

from devicer import DeviceManager, create_in_memory_adapter
from devicer.libs.confidence import calculate_confidence
from devicer.libs.hashing import compare_hashes, get_hash
from tests.fixtures.fingerprints import fp_identical


@pytest.mark.asyncio
async def test_identify_propagates_adapter_errors():
    adapter = create_in_memory_adapter()
    await adapter.init()

    manager = DeviceManager(adapter, dedup_window_ms=0)

    async def fail_find(*_args, **_kwargs):
        raise RuntimeError("DB connection lost")

    adapter.find_candidates = fail_find
    with pytest.raises(RuntimeError, match="DB connection lost"):
        await manager.identify(fp_identical)


@pytest.mark.asyncio
async def test_identify_propagates_save_error(monkeypatch):
    adapter = create_in_memory_adapter()
    await adapter.init()
    manager = DeviceManager(adapter, dedup_window_ms=0)

    async def fail_save(*_args, **_kwargs):
        raise RuntimeError("Disk full")

    monkeypatch.setattr(adapter, "save", fail_save)
    with pytest.raises(RuntimeError, match="Disk full"):
        await manager.identify(fp_identical)


@pytest.mark.asyncio
async def test_identify_propagates_get_history_error(monkeypatch):
    adapter = create_in_memory_adapter()
    await adapter.init()
    manager = DeviceManager(adapter, dedup_window_ms=0)

    await manager.identify(fp_identical)

    async def fail_history(*_args, **_kwargs):
        raise RuntimeError("History read failed")

    monkeypatch.setattr(adapter, "get_history", fail_history)
    with pytest.raises(RuntimeError, match="History read failed"):
        await manager.identify(fp_identical)


def test_hash_edge_cases():
    short = "short"
    assert isinstance(get_hash(short), str)

    assert compare_hashes("", "") == 0
    valid = get_hash("Mozilla/5.0 " * 20)
    assert compare_hashes(valid, "") >= 0
    assert compare_hashes("", valid) >= 0


def test_confidence_with_empty_fingerprints_no_throw():
    assert isinstance(calculate_confidence({}, {}), int)


@pytest.mark.asyncio
async def test_identify_with_empty_fingerprint_creates_device():
    adapter = create_in_memory_adapter()
    await adapter.init()
    manager = DeviceManager(adapter, dedup_window_ms=0)

    result = await manager.identify({})
    assert result.device_id.startswith("dev_")
    assert result.is_new_device is True
