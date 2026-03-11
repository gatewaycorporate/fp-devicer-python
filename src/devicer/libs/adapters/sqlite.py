from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from ..confidence import calculate_confidence
from ...types import DeviceMatch, FPDataSet, StoredFingerprint


class SqliteAdapter:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    async def init(self) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fingerprints (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                user_id TEXT,
                timestamp TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                ip TEXT,
                signals_hash TEXT,
                metadata TEXT,
                match_confidence REAL
            )
            """
        )
        self.conn.commit()

    def _require_conn(self) -> sqlite3.Connection:
        if self.conn is None:
            raise RuntimeError("Adapter not initialized. Call init() first.")
        return self.conn

    async def save(self, snapshot: StoredFingerprint) -> str:
        conn = self._require_conn()
        fingerprint_id = snapshot.id or str(uuid4())
        conn.execute(
            """
            INSERT INTO fingerprints (id, device_id, user_id, timestamp, fingerprint, ip, signals_hash, metadata, match_confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fingerprint_id,
                snapshot.device_id,
                snapshot.user_id,
                snapshot.timestamp.isoformat(),
                json.dumps(snapshot.fingerprint),
                snapshot.ip,
                snapshot.signals_hash,
                json.dumps(snapshot.metadata),
                snapshot.match_confidence,
            ),
        )
        conn.commit()
        return fingerprint_id

    async def get_history(self, device_id: str, limit: int = 50) -> List[StoredFingerprint]:
        conn = self._require_conn()
        rows = conn.execute(
            """
            SELECT id, device_id, user_id, timestamp, fingerprint, ip, signals_hash, metadata, match_confidence
            FROM fingerprints
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (device_id, limit),
        ).fetchall()
        return [
            StoredFingerprint(
                id=row["id"],
                device_id=row["device_id"],
                user_id=row["user_id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                fingerprint=json.loads(row["fingerprint"]),
                ip=row["ip"],
                signals_hash=row["signals_hash"],
                metadata=json.loads(row["metadata"] or "{}"),
                match_confidence=row["match_confidence"],
            )
            for row in rows
        ]

    async def find_candidates(self, query: FPDataSet, min_confidence: float, limit: int = 20) -> List[DeviceMatch]:
        conn = self._require_conn()
        rows = conn.execute(
            """
            SELECT f1.id, f1.device_id, f1.timestamp, f1.fingerprint
            FROM fingerprints f1
            INNER JOIN (
                SELECT device_id, MAX(timestamp) AS max_ts
                FROM fingerprints
                GROUP BY device_id
            ) latest ON latest.device_id = f1.device_id AND latest.max_ts = f1.timestamp
            """
        ).fetchall()

        matches: List[DeviceMatch] = []
        for row in rows:
            fingerprint = json.loads(row["fingerprint"])
            confidence = calculate_confidence(query, fingerprint)
            if confidence >= min_confidence:
                matches.append(
                    DeviceMatch(
                        device_id=row["device_id"],
                        confidence=confidence,
                        last_seen=datetime.fromisoformat(row["timestamp"]),
                    )
                )
        matches.sort(key=lambda item: item.confidence, reverse=True)
        return matches[:limit]

    async def link_to_user(self, device_id: str, user_id: str) -> None:
        conn = self._require_conn()
        conn.execute("UPDATE fingerprints SET user_id = ? WHERE device_id = ?", (user_id, device_id))
        conn.commit()

    async def delete_old_snapshots(self, older_than_days: int) -> int:
        conn = self._require_conn()
        cutoff = (datetime.now(UTC) - timedelta(days=older_than_days)).isoformat()
        cursor = conn.execute("DELETE FROM fingerprints WHERE timestamp < ?", (cutoff,))
        conn.commit()
        return cursor.rowcount

    async def get_all_fingerprints(self) -> List[StoredFingerprint]:
        conn = self._require_conn()
        rows = conn.execute(
            "SELECT id, device_id, user_id, timestamp, fingerprint, ip, signals_hash, metadata, match_confidence FROM fingerprints"
        ).fetchall()
        return [
            StoredFingerprint(
                id=row["id"],
                device_id=row["device_id"],
                user_id=row["user_id"],
                timestamp=datetime.fromisoformat(row["timestamp"]),
                fingerprint=json.loads(row["fingerprint"]),
                ip=row["ip"],
                signals_hash=row["signals_hash"],
                metadata=json.loads(row["metadata"] or "{}"),
                match_confidence=row["match_confidence"],
            )
            for row in rows
        ]

    async def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None


def create_sqlite_adapter(db_path: str) -> SqliteAdapter:
    return SqliteAdapter(db_path)
