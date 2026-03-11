from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Dict, List, Optional


class DefaultLogger:
    def info(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
        print(f"[INFO] {message}", meta or "")

    def warn(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
        print(f"[WARN] {message}", meta or "")

    def error(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
        print(f"[ERROR] {message}", meta or "")

    def debug(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
        print(f"[DEBUG] {message}", meta or "")


@dataclass
class DefaultMetrics:
    counters: Dict[str, float] = field(default_factory=dict)
    histograms: Dict[str, List[float]] = field(default_factory=dict)

    def increment_counter(self, name: str, value: float = 1.0) -> None:
        self.counters[name] = self.counters.get(name, 0.0) + value

    def record_histogram(self, name: str, value: float) -> None:
        self.histograms.setdefault(name, []).append(value)

    def record_gauge(self, name: str, value: float) -> None:
        self.counters[name] = value

    def record_identify(
        self,
        duration_ms: float,
        confidence: float,
        is_new_device: bool,
        candidates_count: int,
        matched: bool,
    ) -> None:
        self.increment_counter("identify_total")
        if is_new_device:
            self.increment_counter("new_devices")
        if matched:
            self.increment_counter("matches_total")
        self.record_histogram("identify_latency_ms", duration_ms)
        self.record_histogram("confidence_scores", confidence)
        self.record_gauge("candidates_per_identify", candidates_count)
        self.record_gauge("avg_confidence", confidence)

    def get_summary(self) -> Dict[str, Any]:
        latencies = self.histograms.get("identify_latency_ms", [])
        return {
            "counters": dict(self.counters),
            "avg_latency": mean(latencies) if latencies else 0.0,
        }


default_logger = DefaultLogger()
default_metrics = DefaultMetrics()
