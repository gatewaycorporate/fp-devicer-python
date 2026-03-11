import types
import uuid
from datetime import UTC, datetime

import pytest

from devicer.libs.adapters.redis import create_redis_adapter
from devicer.types import StoredFingerprint
from tests.fixtures.fingerprints import fp_identical, fp_very_similar


class _FakePipe:
    def __init__(self, client):
        self.client = client
        self.ops = []

    def hset(self, key, field, value):
        self.ops.append(("hset", key, field, value))
        return self

    def expire(self, key, ttl):
        self.ops.append(("expire", key, ttl))
        return self

    def set(self, key, value):
        self.ops.append(("set", key, value))
        return self

    async def execute(self):
        for op in self.ops:
            if op[0] == "hset":
                _, key, field, value = op
                self.client.hashes.setdefault(key, {})[field] = value
            elif op[0] == "set":
                _, key, value = op
                self.client.strings[key] = value
        return []


class _FakeRedis:
    def __init__(self):
        self.sets = {}
        self.hashes = {}
        self.strings = {}

    async def sadd(self, key, member):
        self.sets.setdefault(key, set()).add(member)

    def pipeline(self):
        return _FakePipe(self)

    async def hvals(self, key):
        return list(self.hashes.get(key, {}).values())

    async def smembers(self, key):
        return self.sets.get(key, set())

    async def sinter(self, keys):
        pools = [self.sets.get(key, set()) for key in keys]
        if not pools:
            return set()
        result = set(pools[0])
        for pool in pools[1:]:
            result.intersection_update(pool)
        return result

    async def get(self, key):
        return self.strings.get(key)

    async def hgetall(self, key):
        return self.hashes.get(key, {})

    async def scan(self, cursor=0, match=None, count=100):
        keys = [key for key in self.hashes.keys() if match is None or key.startswith(match.replace("*", ""))]
        return 0, keys

    async def close(self):
        return None


@pytest.mark.asyncio
async def test_redis_adapter_equivalent_flow(monkeypatch):
    fake_client = _FakeRedis()
    fake_asyncio_module = types.SimpleNamespace(from_url=lambda *args, **kwargs: fake_client)
    fake_redis_package = types.SimpleNamespace(asyncio=fake_asyncio_module)
    monkeypatch.setitem(__import__("sys").modules, "redis", fake_redis_package)
    monkeypatch.setitem(__import__("sys").modules, "redis.asyncio", fake_asyncio_module)

    adapter = create_redis_adapter("redis://localhost:6379")
    await adapter.init()

    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_a", timestamp=datetime.now(UTC), fingerprint=fp_identical))
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_b", timestamp=datetime.now(UTC), fingerprint=fp_very_similar))

    history = await adapter.get_history("dev_a", 10)
    assert len(history) == 1

    candidates = await adapter.find_candidates(fp_identical, 70, 5)
    assert len(candidates) >= 1

    await adapter.link_to_user("dev_a", "user_999")
    assert await adapter.delete_old_snapshots(30) == 0

    all_entries = await adapter.get_all_fingerprints()
    assert len(all_entries) >= 2
    await adapter.close()
