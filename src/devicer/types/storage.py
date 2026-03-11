from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol

from .data import FPDataSet


@dataclass
class StoredFingerprint:
    id: str
    device_id: str
    timestamp: datetime
    fingerprint: FPDataSet
    user_id: Optional[str] = None
    ip: Optional[str] = None
    signals_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    match_confidence: Optional[float] = None


@dataclass
class DeviceMatch:
    device_id: str
    confidence: float
    last_seen: datetime


class StorageAdapter(Protocol):
    async def init(self) -> None: ...

    async def save(self, snapshot: StoredFingerprint) -> str: ...

    async def get_history(self, device_id: str, limit: int = 50) -> List[StoredFingerprint]: ...

    async def find_candidates(self, query: FPDataSet, min_confidence: float, limit: int = 20) -> List[DeviceMatch]: ...

    async def link_to_user(self, device_id: str, user_id: str) -> None: ...

    async def delete_old_snapshots(self, older_than_days: int) -> int: ...

    async def get_all_fingerprints(self) -> List[StoredFingerprint]: ...

    async def close(self) -> None: ...
