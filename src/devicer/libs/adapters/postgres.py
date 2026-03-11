from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from ..confidence import calculate_confidence
from ...types import DeviceMatch, FPDataSet, StoredFingerprint


class PostgresAdapter:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self.conn = None

    async def init(self) -> None:
        try:
            import psycopg  # type: ignore
        except Exception as exc:
            raise RuntimeError("Postgres adapter requires optional dependency 'psycopg'") from exc

        self.conn = psycopg.connect(self.dsn)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fingerprints (
                id TEXT PRIMARY KEY,
                device_id TEXT NOT NULL,
                user_id TEXT,
                timestamp TEXT NOT NULL,
                fingerprint JSONB NOT NULL,
                ip TEXT,
                signals_hash TEXT,
                metadata JSONB,
                match_confidence DOUBLE PRECISION
            )
            """
        )
        self.conn.commit()

    def _require_conn(self):
        if self.conn is None:
            raise RuntimeError("Adapter not initialized. Call init() first.")
        return self.conn

    async def save(self, snapshot: StoredFingerprint) -> str:
        conn = self._require_conn()
        fingerprint_id = snapshot.id or str(uuid4())
        conn.execute(
            """
            INSERT INTO fingerprints (id, device_id, user_id, timestamp, fingerprint, ip, signals_hash, metadata, match_confidence)
            VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s)
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
            WHERE device_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (device_id, limit),
        ).fetchall()

        return [
            StoredFingerprint(
                id=row[0],
                device_id=row[1],
                user_id=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                fingerprint=row[4],
                ip=row[5],
                signals_hash=row[6],
                metadata=row[7] or {},
                match_confidence=row[8],
            )
            for row in rows
        ]

    async def find_candidates(self, query: FPDataSet, min_confidence: float, limit: int = 20) -> List[DeviceMatch]:
        conn = self._require_conn()
        rows = conn.execute(
            """
            SELECT f.id, f.device_id, f.timestamp, f.fingerprint
            FROM fingerprints f
            INNER JOIN (
              SELECT device_id, MAX(timestamp) AS max_ts
              FROM fingerprints
              GROUP BY device_id
            ) latest ON latest.device_id = f.device_id AND latest.max_ts = f.timestamp
            """
        ).fetchall()

        candidates: List[DeviceMatch] = []
        for row in rows:
            score = calculate_confidence(query, row[3])
            if score >= min_confidence:
                candidates.append(
                    DeviceMatch(
                        device_id=row[1],
                        confidence=score,
                        last_seen=datetime.fromisoformat(row[2]),
                    )
                )
        candidates.sort(key=lambda item: item.confidence, reverse=True)
        return candidates[:limit]

    async def link_to_user(self, device_id: str, user_id: str) -> None:
        conn = self._require_conn()
        conn.execute("UPDATE fingerprints SET user_id = %s WHERE device_id = %s", (user_id, device_id))
        conn.commit()

    async def delete_old_snapshots(self, older_than_days: int) -> int:
        conn = self._require_conn()
        cutoff = (datetime.now(UTC) - timedelta(days=older_than_days)).isoformat()
        cursor = conn.execute("DELETE FROM fingerprints WHERE timestamp < %s", (cutoff,))
        conn.commit()
        return cursor.rowcount if hasattr(cursor, "rowcount") else 0

    async def get_all_fingerprints(self) -> List[StoredFingerprint]:
        conn = self._require_conn()
        rows = conn.execute(
            "SELECT id, device_id, user_id, timestamp, fingerprint, ip, signals_hash, metadata, match_confidence FROM fingerprints"
        ).fetchall()

        return [
            StoredFingerprint(
                id=row[0],
                device_id=row[1],
                user_id=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                fingerprint=row[4],
                ip=row[5],
                signals_hash=row[6],
                metadata=row[7] or {},
                match_confidence=row[8],
            )
            for row in rows
        ]

    async def close(self) -> None:
        if self.conn is not None:
            self.conn.close()
            self.conn = None


def create_postgres_adapter(dsn: str) -> PostgresAdapter:
    return PostgresAdapter(dsn)
