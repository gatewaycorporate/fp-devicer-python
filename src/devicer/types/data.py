from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypedDict, Union


class FPUserDataSet(TypedDict, total=False):
    userAgent: str
    platform: str
    timezone: str
    language: str
    languages: List[str]
    cookieEnabled: bool
    doNotTrack: Union[str, bool]
    hardwareConcurrency: int
    deviceMemory: Union[int, str]
    product: str
    productSub: str
    vendor: str
    vendorSub: str
    appName: str
    appVersion: str
    appCodeName: str
    appMinorVersion: str
    buildID: str
    plugins: List[Dict[str, str]]
    mimeTypes: List[Dict[str, str]]
    screen: Dict[str, Any]
    fonts: List[str]
    canvas: str
    webgl: str
    audio: str
    highEntropyValues: Dict[str, Any]


FPDataSet = Dict[str, Any]
Comparator = Callable[[Any, Any, Optional[str]], float]


@dataclass(frozen=True)
class ComparisonOptions:
    weights: Optional[Dict[str, float]] = None
    comparators: Optional[Dict[str, Comparator]] = None
    default_weight: float = 5.0
    tlsh_weight: float = 0.30
    max_depth: int = 5
    use_global_registry: bool = True
