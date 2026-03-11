from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from ..types import Comparator


@dataclass
class RegistryState:
    comparators: Dict[str, Comparator] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    default_weight: float = 5.0


_registry = RegistryState()
_defaults_initialized = False
_initializing_defaults = False


def _ensure_defaults() -> None:
    global _defaults_initialized, _initializing_defaults
    if _defaults_initialized or _initializing_defaults:
        return
    _initializing_defaults = True
    from .default_plugins import initialize_default_registry
    try:
        initialize_default_registry()
        _defaults_initialized = True
    finally:
        _initializing_defaults = False


def register_comparator(path: str, comparator: Comparator) -> None:
    if not _defaults_initialized and not _initializing_defaults:
        _ensure_defaults()
    if not callable(comparator):
        raise TypeError("Comparator must be callable")
    _registry.comparators[path] = comparator


def register_weight(path: str, weight: float) -> None:
    if not _defaults_initialized and not _initializing_defaults:
        _ensure_defaults()
    if weight < 0:
        raise ValueError("Weight must be non-negative")
    _registry.weights[path] = float(weight)


def register_plugin(path: str, weight: Optional[float] = None, comparator: Optional[Comparator] = None) -> None:
    if weight is not None:
        register_weight(path, weight)
    if comparator is not None:
        register_comparator(path, comparator)


def unregister_comparator(path: str) -> bool:
    return _registry.comparators.pop(path, None) is not None


def unregister_weight(path: str) -> bool:
    return _registry.weights.pop(path, None) is not None


def set_default_weight(weight: float) -> None:
    if not _defaults_initialized and not _initializing_defaults:
        _ensure_defaults()
    _registry.default_weight = max(0.0, float(weight))


def clear_registry() -> None:
    global _registry, _defaults_initialized
    _registry = RegistryState()
    _defaults_initialized = False


def get_global_registry() -> RegistryState:
    _ensure_defaults()
    return RegistryState(
        comparators=dict(_registry.comparators),
        weights=dict(_registry.weights),
        default_weight=_registry.default_weight,
    )
