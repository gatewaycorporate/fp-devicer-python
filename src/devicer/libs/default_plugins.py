from __future__ import annotations

from .comparators import jaccard_similarity, levenshtein_similarity, screen_similarity
from .registry import register_plugin


_BUILT_IN_PLUGINS = (
    ("userAgent", 20.0, lambda a, b, _p=None: levenshtein_similarity(str(a or "").lower(), str(b or "").lower())),
    ("platform", 15.0, lambda a, b, _p=None: levenshtein_similarity(str(a or "").lower(), str(b or "").lower())),
    ("fonts", 15.0, lambda a, b, _p=None: jaccard_similarity(a if isinstance(a, list) else [], b if isinstance(b, list) else [])),
    ("languages", 20.0, lambda a, b, _p=None: jaccard_similarity(a if isinstance(a, list) else [], b if isinstance(b, list) else [])),
    ("plugins", 15.0, lambda a, b, _p=None: jaccard_similarity(a if isinstance(a, list) else [], b if isinstance(b, list) else [])),
    ("mimeTypes", 15.0, lambda a, b, _p=None: jaccard_similarity(a if isinstance(a, list) else [], b if isinstance(b, list) else [])),
    ("screen", 10.0, lambda a, b, _p=None: screen_similarity(a, b)),
    ("canvas", 30.0, lambda a, b, _p=None: 1.0 if str(a or "") == str(b or "") else 0.0),
    ("webgl", 25.0, lambda a, b, _p=None: 1.0 if str(a or "") == str(b or "") else 0.0),
    ("audio", 25.0, lambda a, b, _p=None: 1.0 if str(a or "") == str(b or "") else 0.0),
)


def initialize_default_registry() -> None:
    for path, weight, comparator in _BUILT_IN_PLUGINS:
        register_plugin(path, weight=weight, comparator=comparator)
