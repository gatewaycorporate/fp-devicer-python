from __future__ import annotations

from typing import Any


def levenshtein_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    max_len = max(len(a), len(b))
    distance = abs(len(a) - len(b))
    min_len = min(len(a), len(b))
    for index in range(min_len):
        if a[index] != b[index]:
            distance += 1
    return max(0.0, 1.0 - (distance / max_len))


def jaccard_similarity(a: Any, b: Any) -> float:
    list_a = a if isinstance(a, list) else []
    list_b = b if isinstance(b, list) else []
    set_a = {str(item) for item in list_a}
    set_b = {str(item) for item in list_b}
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return 0.0 if union == 0 else intersection / union


def numeric_proximity(a: Any, b: Any) -> float:
    if a is None or b is None:
        return 0.5
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return 1.0 if a == b else 0.0
    if a == b:
        return 1.0
    value_range = max(abs(a), abs(b), 1)
    return max(0.0, 1.0 - abs(a - b) / value_range)


def screen_similarity(screen1: Any, screen2: Any) -> float:
    if not isinstance(screen1, dict) or not isinstance(screen2, dict):
        return 0.5
    width = numeric_proximity(screen1.get("width"), screen2.get("width"))
    height = numeric_proximity(screen1.get("height"), screen2.get("height"))
    color_depth = numeric_proximity(screen1.get("colorDepth"), screen2.get("colorDepth"))
    pixel_depth = numeric_proximity(screen1.get("pixelDepth"), screen2.get("pixelDepth"))
    orientation = 1.0 if screen1.get("orientation", {}).get("type") == screen2.get("orientation", {}).get("type") else 0.0
    return (width + height + color_depth + pixel_depth + orientation) / 5.0
