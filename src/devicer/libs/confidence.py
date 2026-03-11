from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .hashing import canonicalized_stringify, compare_hashes, get_hash
from .registry import get_global_registry
from ..types import Comparator, ComparisonOptions, FPDataSet


DEFAULT_WEIGHTS: Dict[str, float] = {
    "userAgent": 10,
    "platform": 20,
    "timezone": 10,
    "language": 15,
    "languages": 20,
    "cookieEnabled": 5,
    "doNotTrack": 5,
    "hardwareConcurrency": 5,
    "deviceMemory": 5,
    "product": 5,
    "productSub": 5,
    "vendor": 5,
    "vendorSub": 5,
    "appName": 5,
    "appVersion": 5,
    "appCodeName": 5,
    "appMinorVersion": 5,
    "buildID": 5,
    "plugins": 15,
    "mimeTypes": 15,
    "screen": 10,
    "fonts": 15,
    "canvas": 30,
    "webgl": 25,
    "audio": 25,
    "highEntropyValues": 20,
}


def _js_round(value: float) -> int:
    if value >= 0:
        return int(value + 0.5)
    return -int(abs(value) + 0.5)


def _default_comparator(a: Any, b: Any, _path: Optional[str] = None) -> float:
    return 1.0 if a == b else 0.0


@dataclass
class ConfidenceCalculator:
    options: ComparisonOptions

    def __post_init__(self) -> None:
        local_weights = self.options.weights or {}
        local_comparators = self.options.comparators or {}
        if self.options.use_global_registry:
            global_registry = get_global_registry()
            self.weights = {**global_registry.weights, **DEFAULT_WEIGHTS, **local_weights}
            self.comparators = {**global_registry.comparators, **local_comparators}
            self.default_weight = self.options.default_weight or global_registry.default_weight
        else:
            self.weights = {**DEFAULT_WEIGHTS, **local_weights}
            self.comparators = dict(local_comparators)
            self.default_weight = self.options.default_weight

    def _get_weight(self, path: str) -> float:
        return float(self.weights.get(path, self.default_weight))

    def _get_comparator(self, path: str) -> Comparator:
        return self.comparators.get(path, _default_comparator)

    def _compare_recursive(self, value1: Any, value2: Any, path: str = "", depth: int = 0) -> Tuple[float, float]:
        if depth > self.options.max_depth:
            return 0.0, 0.0
        if value1 is None or value2 is None:
            return 0.0, 0.0

        if not isinstance(value1, (dict, list)) or not isinstance(value2, (dict, list)):
            comparator = self._get_comparator(path)
            similarity = max(0.0, min(1.0, float(comparator(value1, value2, path))))
            weight = self._get_weight(path)
            return weight, weight * similarity

        if isinstance(value1, list) and isinstance(value2, list):
            total = 0.0
            matched = 0.0
            for index in range(min(len(value1), len(value2))):
                child_path = f"{path}[{index}]"
                child_total, child_matched = self._compare_recursive(value1[index], value2[index], child_path, depth + 1)
                total += child_total
                matched += child_matched
            return total, matched

        if isinstance(value1, dict) and isinstance(value2, dict):
            total = 0.0
            matched = 0.0
            keys = set(value1.keys()).union(set(value2.keys()))
            for key in keys:
                child_path = f"{path}.{key}" if path else str(key)
                child_total, child_matched = self._compare_recursive(value1.get(key), value2.get(key), child_path, depth + 1)
                total += child_total
                matched += child_matched
            return total, matched

        return 0.0, 0.0

    def calculate_confidence(self, data1: FPDataSet, data2: FPDataSet) -> int:
        total_weight, matched_weight = self._compare_recursive(data1, data2)
        structural_score = matched_weight / total_weight if total_weight > 0 else 0.0

        tlsh_score = 1.0
        tlsh_weight = max(0.0, min(1.0, self.options.tlsh_weight))
        if tlsh_weight > 0:
            tlsh_max_distance = 300
            hash1 = get_hash(canonicalized_stringify(data1))
            hash2 = get_hash(canonicalized_stringify(data2))
            difference = compare_hashes(hash1, hash2)
            tlsh_score = max(0.0, (tlsh_max_distance - difference) / tlsh_max_distance)

        final_score = structural_score * (1.0 - tlsh_weight) + tlsh_score * tlsh_weight
        return _js_round(max(0.0, min(100.0, final_score * 100.0)))


def create_confidence_calculator(user_options: Optional[ComparisonOptions] = None) -> ConfidenceCalculator:
    return ConfidenceCalculator(options=user_options or ComparisonOptions())


def calculate_confidence(data1: FPDataSet, data2: FPDataSet) -> int:
    return create_confidence_calculator().calculate_confidence(data1, data2)