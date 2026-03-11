from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Dict, List

from ..confidence import calculate_confidence
from ...types import DeviceMatch, FPDataSet, StoredFingerprint


class InMemoryAdapter:
    def __init__(self) -> None:
        self._store: Dict[str, List[StoredFingerprint]] = {}

    async def init(self) -> None:
        return None

    async def save(self, snapshot: StoredFingerprint) -> str:
        self._store.setdefault(snapshot.device_id, []).append(snapshot)
        return snapshot.id

    async def get_history(self, device_id: str, limit: int = 50) -> List[StoredFingerprint]:
        history = self._store.get(device_id, [])
        return sorted(history, key=lambda item: item.timestamp, reverse=True)[:limit]

    async def find_candidates(self, query: FPDataSet, min_confidence: float, limit: int = 20) -> List[DeviceMatch]:
        matches: List[DeviceMatch] = []
        for device_id, snapshots in self._store.items():
            if not snapshots:
                continue
            latest = max(snapshots, key=lambda item: item.timestamp)
            confidence = calculate_confidence(query, latest.fingerprint)
            if confidence >= min_confidence:
                matches.append(DeviceMatch(device_id=device_id, confidence=confidence, last_seen=latest.timestamp))
        matches.sort(key=lambda item: item.confidence, reverse=True)
        return matches[:limit]

    async def link_to_user(self, device_id: str, user_id: str) -> None:
        for snapshot in self._store.get(device_id, []):
            snapshot.user_id = user_id

    async def delete_old_snapshots(self, older_than_days: int) -> int:
        cutoff = datetime.now(UTC) - timedelta(days=older_than_days)
        deleted = 0
        for device_id, history in list(self._store.items()):
            retained = [snapshot for snapshot in history if snapshot.timestamp >= cutoff]
            deleted += len(history) - len(retained)
            if retained:
                self._store[device_id] = retained
            else:
                self._store.pop(device_id, None)
        return deleted

    async def get_all_fingerprints(self) -> List[StoredFingerprint]:
        all_snapshots: List[StoredFingerprint] = []
        for history in self._store.values():
            all_snapshots.extend(history)
        return list(all_snapshots)

    async def close(self) -> None:
        return None


def create_in_memory_adapter() -> InMemoryAdapter:
    return InMemoryAdapter()
