from __future__ import annotations

import hashlib
from typing import Any

try:
    import tlsh  # type: ignore
except Exception:
    tlsh = None


def canonicalized_stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float, str)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(canonicalized_stringify(item) for item in value) + "]"
    if isinstance(value, dict):
        keys = sorted(str(k) for k in value.keys())
        return "{" + ",".join(f"{key}:{canonicalized_stringify(value.get(key))}" for key in keys) + "}"
    return str(value)


def get_hash(data: Any) -> str:
    payload = data if isinstance(data, str) else canonicalized_stringify(data)
    if tlsh is not None:
        return tlsh.hash(payload.encode("utf-8"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def compare_hashes(hash1: str, hash2: str) -> int:
    if tlsh is not None:
        return tlsh.diff(hash1, hash2)
    return sum(0 if left == right else 1 for left, right in zip(hash1, hash2)) + abs(len(hash1) - len(hash2))


def get_tlsh_hash(data: bytes) -> str:
    if tlsh is not None:
        return tlsh.hash(data)
    return hashlib.sha256(data).hexdigest()


def get_hash_difference(hash1: str, hash2: str) -> int:
    return compare_hashes(hash1, hash2)