from __future__ import annotations

import json
from datetime import datetime
from typing import List
from uuid import uuid4

from ..confidence import calculate_confidence
from ...types import DeviceMatch, FPDataSet, StoredFingerprint


class RedisAdapter:
    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        self.redis_url = redis_url
        self.redis = None

    async def init(self) -> None:
        try:
            import redis.asyncio as redis  # type: ignore
        except Exception as exc:
            raise RuntimeError("Redis adapter requires optional dependency 'redis'") from exc

        self.redis = redis.from_url(self.redis_url, decode_responses=True)

    def _require_redis(self):
        if self.redis is None:
            raise RuntimeError("Adapter not initialized. Call init() first.")
        return self.redis

    async def save(self, snapshot: StoredFingerprint) -> str:
        redis = self._require_redis()
        snapshot_id = str(uuid4())
        device_key = f"fp:device:{snapshot.device_id}"

        payload = json.dumps(
            {
                "id": snapshot.id,
                "device_id": snapshot.device_id,
                "user_id": snapshot.user_id,
                "timestamp": snapshot.timestamp.isoformat(),
                "fingerprint": snapshot.fingerprint,
                "ip": snapshot.ip,
                "signals_hash": snapshot.signals_hash,
                "metadata": snapshot.metadata,
                "match_confidence": snapshot.match_confidence,
            }
        )

        await redis.sadd(f"idx:platform:{snapshot.fingerprint.get('platform')}", snapshot.device_id)
        await redis.sadd(f"idx:deviceMemory:{snapshot.fingerprint.get('deviceMemory')}", snapshot.device_id)
        await redis.sadd(
            f"idx:hardwareConcurrency:{snapshot.fingerprint.get('hardwareConcurrency')}",
            snapshot.device_id,
        )

        tx = redis.pipeline()
        tx.hset(device_key, snapshot_id, payload)
        tx.expire(device_key, 60 * 60 * 24 * 90)
        tx.set(f"fp:latest:{snapshot.device_id}", payload)
        await tx.execute()
        return snapshot_id

    async def get_history(self, device_id: str, limit: int = 50) -> List[StoredFingerprint]:
        redis = self._require_redis()
        raw = await redis.hvals(f"fp:device:{device_id}")
        snapshots = [self._decode_snapshot(item) for item in raw]
        snapshots.sort(key=lambda item: item.timestamp, reverse=True)
        return snapshots[:limit]

    async def find_candidates(self, query: FPDataSet, min_confidence: float, limit: int = 20) -> List[DeviceMatch]:
        redis = self._require_redis()
        index_keys = []
        if query.get("platform") is not None:
            index_keys.append(f"idx:platform:{query.get('platform')}")
        if query.get("deviceMemory") is not None:
            index_keys.append(f"idx:deviceMemory:{query.get('deviceMemory')}")
        if query.get("hardwareConcurrency") is not None:
            index_keys.append(f"idx:hardwareConcurrency:{query.get('hardwareConcurrency')}")

        if not index_keys:
            return []

        if len(index_keys) == 1:
            device_ids = await redis.smembers(index_keys[0])
        else:
            device_ids = await redis.sinter(index_keys)

        device_ids = list(device_ids)[: limit * 2]
        candidates: List[DeviceMatch] = []
        for device_id in device_ids:
            raw_latest = await redis.get(f"fp:latest:{device_id}")
            if not raw_latest:
                continue
            snapshot = self._decode_snapshot(raw_latest)
            score = calculate_confidence(query, snapshot.fingerprint)
            if score >= min_confidence:
                candidates.append(
                    DeviceMatch(
                        device_id=device_id,
                        confidence=score,
                        last_seen=snapshot.timestamp,
                    )
                )

        candidates.sort(key=lambda item: item.confidence, reverse=True)
        return candidates[:limit]

    async def link_to_user(self, device_id: str, user_id: str) -> None:
        redis = self._require_redis()
        history = await redis.hgetall(f"fp:device:{device_id}")
        tx = redis.pipeline()
        for key, raw in history.items():
            data = json.loads(raw)
            data["user_id"] = user_id
            tx.hset(f"fp:device:{device_id}", key, json.dumps(data))
        await tx.execute()

    async def delete_old_snapshots(self, older_than_days: int) -> int:
        _ = older_than_days
        return 0

    async def get_all_fingerprints(self) -> List[StoredFingerprint]:
        redis = self._require_redis()
        cursor = 0
        all_snapshots: List[StoredFingerprint] = []

        while True:
            cursor, keys = await redis.scan(cursor=cursor, match="fp:device:*", count=100)
            for key in keys:
                values = await redis.hvals(key)
                all_snapshots.extend(self._decode_snapshot(item) for item in values)
            if cursor == 0:
                break

        return all_snapshots

    async def close(self) -> None:
        if self.redis is not None:
            await self.redis.close()
            self.redis = None

    @staticmethod
    def _decode_snapshot(raw: str) -> StoredFingerprint:
        parsed = json.loads(raw)
        return StoredFingerprint(
            id=parsed["id"],
            device_id=parsed["device_id"],
            user_id=parsed.get("user_id"),
            timestamp=datetime.fromisoformat(parsed["timestamp"]),
            fingerprint=parsed["fingerprint"],
            ip=parsed.get("ip"),
            signals_hash=parsed.get("signals_hash"),
            metadata=parsed.get("metadata") or {},
            match_confidence=parsed.get("match_confidence"),
        )


def create_redis_adapter(redis_url: str = "redis://localhost:6379") -> RedisAdapter:
    return RedisAdapter(redis_url=redis_url)
