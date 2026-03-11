from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


class Logger(Protocol):
    def info(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None: ...

    def warn(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None: ...

    def error(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None: ...

    def debug(self, message: str, meta: Optional[Dict[str, Any]] = None) -> None: ...


class Metrics(Protocol):
    def increment_counter(self, name: str, value: float = 1.0) -> None: ...

    def record_histogram(self, name: str, value: float) -> None: ...

    def record_gauge(self, name: str, value: float) -> None: ...

    def record_identify(
        self,
        duration_ms: float,
        confidence: float,
        is_new_device: bool,
        candidates_count: int,
        matched: bool,
    ) -> None: ...

    def get_summary(self) -> Dict[str, Any]: ...


@dataclass(frozen=True)
class ObservabilityOptions:
    logger: Optional[Logger] = None
    metrics: Optional[Metrics] = None
