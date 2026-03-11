import json
import types
import uuid
from datetime import UTC, datetime, timedelta

import pytest

from devicer.libs.adapters.postgres import create_postgres_adapter
from devicer.types import StoredFingerprint
from tests.fixtures.fingerprints import fp_identical, fp_very_similar


class _FakeCursor:
    def __init__(self, rows=None, rowcount=0):
        self._rows = rows or []
        self.rowcount = rowcount

    def fetchall(self):
        return list(self._rows)


class _FakeConn:
    def __init__(self):
        self.rows = []

    def execute(self, query, params=None):
        text = str(query).lower().strip()
        params = params or ()
        if text.startswith("create table"):
            return _FakeCursor()
        if text.startswith("insert into fingerprints"):
            self.rows.append(
                {
                    "id": params[0],
                    "device_id": params[1],
                    "user_id": params[2],
                    "timestamp": params[3],
                    "fingerprint": json.loads(params[4]),
                    "ip": params[5],
                    "signals_hash": params[6],
                    "metadata": json.loads(params[7]),
                    "match_confidence": params[8],
                }
            )
            return _FakeCursor()
        if "where device_id = %s" in text:
            device_id = params[0]
            limit = params[1]
            rows = [r for r in self.rows if r["device_id"] == device_id][:limit]
            tuples = [(r["id"], r["device_id"], r["user_id"], r["timestamp"], r["fingerprint"], r["ip"], r["signals_hash"], r["metadata"], r["match_confidence"]) for r in rows]
            return _FakeCursor(tuples)
        if text.startswith("select f.id"):
            latest = {}
            for row in self.rows:
                latest[row["device_id"]] = row
            tuples = [(r["id"], r["device_id"], r["timestamp"], r["fingerprint"]) for r in latest.values()]
            return _FakeCursor(tuples)
        if text.startswith("update fingerprints set user_id"):
            user_id, device_id = params
            for row in self.rows:
                if row["device_id"] == device_id:
                    row["user_id"] = user_id
            return _FakeCursor()
        if text.startswith("delete from fingerprints"):
            cutoff = params[0]
            before = len(self.rows)
            self.rows = [r for r in self.rows if r["timestamp"] >= cutoff]
            return _FakeCursor(rowcount=before - len(self.rows))
        if text.startswith("select id, device_id"):
            tuples = [(r["id"], r["device_id"], r["user_id"], r["timestamp"], r["fingerprint"], r["ip"], r["signals_hash"], r["metadata"], r["match_confidence"]) for r in self.rows]
            return _FakeCursor(tuples)
        return _FakeCursor()

    def commit(self):
        return None

    def close(self):
        return None


@pytest.mark.asyncio
async def test_postgres_adapter_equivalent_flow(monkeypatch):
    fake_module = types.SimpleNamespace(connect=lambda _dsn: _FakeConn())
    monkeypatch.setitem(__import__("sys").modules, "psycopg", fake_module)

    adapter = create_postgres_adapter("postgresql://localhost/test")
    await adapter.init()

    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_a", timestamp=datetime.now(UTC), fingerprint=fp_identical))
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="dev_b", timestamp=datetime.now(UTC), fingerprint=fp_very_similar))

    history = await adapter.get_history("dev_a", 10)
    assert len(history) == 1

    candidates = await adapter.find_candidates(fp_identical, 70, 5)
    assert len(candidates) >= 1

    old = datetime.now(UTC) - timedelta(days=31)
    await adapter.save(StoredFingerprint(id=str(uuid.uuid4()), device_id="old_dev", timestamp=old, fingerprint=fp_identical))
    deleted = await adapter.delete_old_snapshots(30)
    assert deleted >= 1

    all_entries = await adapter.get_all_fingerprints()
    assert len(all_entries) >= 2
    await adapter.close()
