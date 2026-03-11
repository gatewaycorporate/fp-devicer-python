from .comparators import jaccard_similarity, levenshtein_similarity, numeric_proximity, screen_similarity
from .confidence import DEFAULT_WEIGHTS, calculate_confidence, create_confidence_calculator
from .default_observability import DefaultLogger, DefaultMetrics, default_logger, default_metrics
from .default_plugins import initialize_default_registry
from .hashing import canonicalized_stringify, compare_hashes, get_hash, get_hash_difference, get_tlsh_hash
from .registry import (
    clear_registry,
    get_global_registry,
    register_comparator,
    register_plugin,
    register_weight,
    set_default_weight,
    unregister_comparator,
    unregister_weight,
)

__all__ = [
    "DEFAULT_WEIGHTS",
    "DefaultLogger",
    "DefaultMetrics",
    "calculate_confidence",
    "create_confidence_calculator",
    "canonicalized_stringify",
    "compare_hashes",
    "get_hash",
    "get_hash_difference",
    "get_tlsh_hash",
    "jaccard_similarity",
    "levenshtein_similarity",
    "numeric_proximity",
    "screen_similarity",
    "default_logger",
    "default_metrics",
    "clear_registry",
    "get_global_registry",
    "initialize_default_registry",
    "register_comparator",
    "register_plugin",
    "register_weight",
    "set_default_weight",
    "unregister_comparator",
    "unregister_weight",
]
