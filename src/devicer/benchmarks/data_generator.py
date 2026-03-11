from __future__ import annotations

import copy
import random
from dataclasses import dataclass
from uuid import uuid4
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class LabeledFingerprint:
    id: str
    data: Dict[str, Any]
    device_label: str
    is_attractor: bool


class _Prng:
    def __init__(self, seed: int) -> None:
        self._state = seed & 0xFFFFFFFF

    def next(self) -> float:
        self._state = (1664525 * self._state + 1013904223) & 0xFFFFFFFF
        return self._state / 0x100000000

    def int(self, min_value: int, max_value: int) -> int:
        return min_value + int(self.next() * (max_value - min_value + 1))

    def pick(self, values: List[Any]) -> Any:
        return values[self.int(0, len(values) - 1)]

    def bool(self, prob: float = 0.5) -> bool:
        return self.next() < prob

    def shuffle(self, values: List[Any]) -> List[Any]:
        cloned = list(values)
        for index in range(len(cloned) - 1, 0, -1):
            swap_index = self.int(0, index)
            cloned[index], cloned[swap_index] = cloned[swap_index], cloned[index]
        return cloned


_PLATFORMS = [
    {"os": "Windows NT 10.0; Win64; x64", "platform": "Win32", "appOs": "Windows", "mobile": False},
    {"os": "Windows NT 11.0; Win64; x64", "platform": "Win32", "appOs": "Windows", "mobile": False},
    {"os": "Macintosh; Intel Mac OS X 10_15_7", "platform": "MacIntel", "appOs": "Macintosh", "mobile": False},
    {"os": "Macintosh; Intel Mac OS X 13_6", "platform": "MacIntel", "appOs": "Macintosh", "mobile": False},
    {"os": "Macintosh; ARM Mac OS X 14_0", "platform": "MacIntel", "appOs": "Macintosh", "mobile": False},
    {"os": "X11; Linux x86_64", "platform": "Linux x86_64", "appOs": "X11", "mobile": False},
    {"os": "X11; Ubuntu; Linux x86_64", "platform": "Linux x86_64", "appOs": "X11", "mobile": False},
    {"os": "Linux; Android 13", "platform": "Linux armv8l", "appOs": "Android", "mobile": True},
    {"os": "Linux; Android 14", "platform": "Linux armv8l", "appOs": "Android", "mobile": True},
    {"os": "iPhone OS 17_0 like Mac OS X", "platform": "iPhone", "appOs": "iPhone", "mobile": True},
    {"os": "iPhone OS 16_0 like Mac OS X", "platform": "iPhone", "appOs": "iPhone", "mobile": True},
]

_BROWSER_PROFILES = [
    {
        "ua": lambda plat, ver: f"Mozilla/5.0 ({plat['os']}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{ver}.0.0.0 Safari/537.36",
        "vendor": "Google Inc.",
        "appName": "Netscape",
        "product": "Gecko",
        "productSub": "20100101",
    },
    {
        "ua": lambda plat, ver: f"Mozilla/5.0 ({plat['os']}; rv:{ver}.0) Gecko/20100101 Firefox/{ver}.0",
        "vendor": "",
        "appName": "Netscape",
        "product": "Gecko",
        "productSub": "20100101",
    },
    {
        "ua": lambda plat, ver: f"Mozilla/5.0 ({plat['os']}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{ver}.0 Safari/605.1.15",
        "vendor": "Apple Computer, Inc.",
        "appName": "Netscape",
        "product": "Gecko",
        "productSub": "20030107",
    },
]

_CHROME_VERSIONS = [120, 121, 122, 123, 124, 125, 126]
_TIMEZONES = [
    "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
    "America/Sao_Paulo", "Europe/London", "Europe/Paris", "Europe/Berlin",
    "Europe/Moscow", "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata",
    "Australia/Sydney", "Pacific/Auckland",
]
_LANGUAGES_MAP = {
    "en-US": ["en-US", "en"],
    "en-GB": ["en-GB", "en"],
    "fr-FR": ["fr-FR", "fr", "en"],
    "de-DE": ["de-DE", "de", "en"],
    "es-ES": ["es-ES", "es"],
    "ja-JP": ["ja-JP", "ja"],
    "zh-CN": ["zh-CN", "zh"],
    "pt-BR": ["pt-BR", "pt"],
}
_SCREEN_RESOLUTIONS = [
    (1280, 720), (1366, 768), (1440, 900), (1600, 900),
    (1920, 1080), (1920, 1200), (2560, 1080), (2560, 1440),
    (3440, 1440), (3840, 2160), (1024, 768), (1280, 800),
]
_HARDWARE_CONCURRENCY = [2, 4, 6, 8, 10, 12, 16, 20, 24, 32]
_DEVICE_MEMORY = [1, 2, 4, 8, 16, 32]
_FONT_POOL = [
    "Arial", "Arial Black", "Arial Narrow", "Calibri", "Cambria", "Comic Sans MS",
    "Consolas", "Courier New", "Georgia", "Helvetica", "Impact", "Lucida Console",
    "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype", "Segoe UI",
    "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana",
    "Gill Sans", "Optima", "Futura", "Baskerville", "Didot",
    "DejaVu Sans", "Liberation Mono", "Ubuntu", "Noto Sans",
    "Garamond", "Rockwell", "Century Gothic", "Franklin Gothic Medium",
]
_PLUGIN_POOL = [
    {"name": "Chrome PDF Viewer", "description": "Portable Document Format"},
    {"name": "Chromium PDF Viewer", "description": "Portable Document Format"},
    {"name": "Microsoft Edge PDF Viewer", "description": "Portable Document Format"},
    {"name": "WebKit built-in PDF", "description": "Portable Document Format"},
]
_HEV_BRANDS = [
    [{"brand": "Chromium", "version": "124"}, {"brand": "Google Chrome", "version": "124"}, {"brand": "Not-A.Brand", "version": "99"}],
    [{"brand": "Chromium", "version": "122"}, {"brand": "Google Chrome", "version": "122"}, {"brand": "Not-A.Brand", "version": "99"}],
    [{"brand": "Chromium", "version": "120"}, {"brand": "Google Chrome", "version": "120"}, {"brand": "Not-A.Brand", "version": "8"}],
]


def _to_base36(value: int) -> str:
    if value == 0:
        return "0"
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""
    number = value
    while number > 0:
        number, rem = divmod(number, 36)
        result = digits[rem] + result
    return result


def _simple_hash(value: str) -> str:
    acc = 5381
    for char in value:
        acc = ((acc << 5) - acc) + ord(char)
        acc &= 0xFFFFFFFF
    return _to_base36(acc)


def generate_canvas_blob(seed: int, rng: _Prng) -> str:
    stable_rng = _Prng(seed ^ 0xDEADBEEF)
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    raw_stable = "".join(chars[stable_rng.int(0, len(chars) - 1)] for _ in range(200))
    raw_jitter = "".join(chars[rng.int(0, len(chars) - 1)] for _ in range(10))
    return _simple_hash(raw_stable + raw_jitter)


def generate_webgl_blob(seed: int, rng: _Prng) -> str:
    renderers = [
        "ANGLE (NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
        "ANGLE (Apple M1 GPU, Metal)",
        "ANGLE (Apple M2 GPU, Metal)",
        "Mesa/X.org (llvmpipe LLVM 15.0.7 256 bits)",
        "Adreno (TM) 650",
        "Mali-G78 MP14",
    ]
    extensions = [
        "EXT_color_buffer_float", "EXT_float_blend", "EXT_texture_compression_bptc",
        "EXT_texture_compression_rgtc", "EXT_texture_filter_anisotropic",
        "OES_texture_float_linear", "WEBGL_compressed_texture_s3tc",
        "WEBGL_debug_renderer_info", "WEBGL_lose_context", "WEBGL_multi_draw",
    ]
    stable_rng = _Prng(seed ^ 0xCAFE1234)
    renderer = renderers[stable_rng.int(0, len(renderers) - 1)]
    ext_count = rng.int(4, 7)
    shuffled = rng.shuffle(extensions)
    exts = ",".join(shuffled[:ext_count])
    return _simple_hash(f"{renderer}~~{exts}")


def generate_audio_blob(seed: int, rng: _Prng) -> str:
    stable_rng = _Prng(seed ^ 0xABCDEF01)
    int_part = stable_rng.int(100, 999)
    frac_stable = str(stable_rng.int(10000000, 99999999))
    frac_jitter = str(rng.int(1000, 9999))
    return _simple_hash(f"{int_part}.{frac_stable}{frac_jitter}")


def create_attractor_fingerprint(seed: int) -> Dict[str, Any]:
    rng = _Prng(seed * 2654435761)
    plat = next(item for item in _PLATFORMS if item["platform"] == "Win32" and "10.0" in item["os"])
    profile = _BROWSER_PROFILES[0]
    chrome_ver = 124
    lang_key = "en-US"
    languages = _LANGUAGES_MAP[lang_key]

    font_count = rng.int(8, 14)
    fonts = rng.shuffle(_FONT_POOL)[:font_count]
    plugin_count = rng.int(0, 1)
    plugins = rng.shuffle(_PLUGIN_POOL)[:plugin_count]
    mime_types = ([{"type": "application/pdf", "description": "Portable Document Format", "suffixes": "pdf"}] if plugins else [])

    canvas = generate_canvas_blob(seed, rng)
    webgl = generate_webgl_blob(seed, rng)
    audio = generate_audio_blob(seed, rng)

    hev = {
        "architecture": "x64",
        "bitness": "64",
        "brands": _HEV_BRANDS[0],
        "mobile": False,
        "platform": "Windows",
        "platformVersion": f"10.0.{rng.int(19041, 22631)}",
        "uaFullVersion": f"124.0.{rng.int(5000, 6999)}.{rng.int(100, 200)}",
    }

    return {
        "userAgent": profile["ua"](plat, chrome_ver),
        "platform": plat["platform"],
        "timezone": "America/New_York",
        "language": lang_key,
        "languages": languages,
        "cookieEnabled": True,
        "doNotTrack": False,
        "product": "Gecko",
        "productSub": "20100101",
        "vendor": "Google Inc.",
        "vendorSub": "",
        "appName": "Netscape",
        "appVersion": f"5.0 ({plat['appOs']}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
        "appCodeName": "Mozilla",
        "appMinorVersion": "0",
        "buildID": "20240101",
        "hardwareConcurrency": 8,
        "deviceMemory": 8,
        "screen": {
            "width": 1920,
            "height": 1080,
            "colorDepth": 24,
            "pixelDepth": 24,
            "orientation": {"type": "landscape-primary", "angle": 0},
        },
        "fonts": fonts,
        "plugins": plugins,
        "mimeTypes": mime_types,
        "canvas": canvas,
        "webgl": webgl,
        "audio": audio,
        "highEntropyValues": hev,
    }


def create_base_fingerprint(seed: int) -> Dict[str, Any]:
    rng = _Prng(seed * 2654435761)
    plat = rng.pick(_PLATFORMS)
    profile = rng.pick(_BROWSER_PROFILES)
    chrome_ver = rng.pick(_CHROME_VERSIONS)
    timezone = rng.pick(_TIMEZONES)
    lang_key = rng.pick(list(_LANGUAGES_MAP.keys()))
    languages = _LANGUAGES_MAP[lang_key]
    if plat["mobile"]:
        sw, sh = rng.int(320, 480), rng.int(480, 800)
    else:
        sw, sh = rng.pick(_SCREEN_RESOLUTIONS)
    color_depth = rng.pick([24, 30, 32])
    concurrency = rng.pick([4, 8]) if plat["mobile"] else rng.pick(_HARDWARE_CONCURRENCY)
    memory = rng.pick(_DEVICE_MEMORY)

    font_count = rng.int(6, 18)
    fonts = rng.shuffle(_FONT_POOL)[:font_count]
    plugin_count = rng.int(0, 2)
    plugins = rng.shuffle(_PLUGIN_POOL)[:plugin_count]
    mime_types = ([{"type": "application/pdf", "description": "Portable Document Format", "suffixes": "pdf"}] if plugins else [])

    canvas = generate_canvas_blob(seed, rng)
    webgl = generate_webgl_blob(seed, rng)
    audio = generate_audio_blob(seed, rng)

    hev = {
        "architecture": rng.pick(["x86", "x64", "arm"]),
        "bitness": rng.pick(["32", "64"]),
        "brands": rng.pick(_HEV_BRANDS),
        "mobile": plat["mobile"],
        "platform": plat["appOs"],
        "platformVersion": f"{rng.int(10, 15)}.{rng.int(0, 9)}.{rng.int(0, 9)}",
        "uaFullVersion": f"{chrome_ver}.0.{rng.int(5000, 6999)}.{rng.int(100, 200)}",
    }

    return {
        "userAgent": profile["ua"](plat, chrome_ver),
        "platform": plat["platform"],
        "timezone": timezone,
        "language": lang_key,
        "languages": languages,
        "cookieEnabled": rng.bool(0.97),
        "doNotTrack": "1" if rng.bool(0.15) else False,
        "product": profile["product"],
        "productSub": profile["productSub"],
        "vendor": profile["vendor"],
        "vendorSub": "",
        "appName": profile["appName"],
        "appVersion": f"5.0 ({plat['appOs']}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver}.0.0.0 Safari/537.36",
        "appCodeName": "Mozilla",
        "appMinorVersion": "0",
        "buildID": "20240101",
        "hardwareConcurrency": concurrency,
        "deviceMemory": memory,
        "screen": {
            "width": sw,
            "height": sh,
            "colorDepth": color_depth,
            "pixelDepth": color_depth,
            "orientation": {"type": "portrait-primary" if plat["mobile"] else "landscape-primary", "angle": 0},
        },
        "fonts": fonts,
        "plugins": plugins,
        "mimeTypes": mime_types,
        "canvas": canvas,
        "webgl": webgl,
        "audio": audio,
        "highEntropyValues": hev,
    }


def mutate(fingerprint: Dict[str, Any], level: str) -> Dict[str, Any]:
    cloned = copy.deepcopy(fingerprint)
    if level == "low":
        if cloned.get("screen"):
            cloned["screen"]["width"] += round((random.random() - 0.5) * 4)
        canvas = str(cloned.get("canvas", ""))
        cloned["canvas"] = _simple_hash(canvas + str(random.randint(0, 2)))
        if random.random() < 0.4 and cloned.get("fonts"):
            shuffled = list(cloned["fonts"])
            random.shuffle(shuffled)
            cloned["fonts"] = shuffled
    elif level == "medium":
        ua = str(cloned.get("userAgent", ""))
        if "Chrome/" in ua:
            version = int(ua.split("Chrome/")[1].split(".")[0])
            cloned["userAgent"] = ua.replace(f"Chrome/{version}", f"Chrome/{version + random.randint(0, 1)}")
        if random.random() < 0.5 and len(cloned.get("fonts", [])) < len(_FONT_POOL):
            candidates = [item for item in _FONT_POOL if item not in cloned.get("fonts", [])]
            if candidates:
                cloned.setdefault("fonts", []).append(random.choice(candidates))
        elif len(cloned.get("fonts", [])) > 3:
            cloned["fonts"].pop(random.randint(0, len(cloned["fonts"]) - 1))
        if random.random() < 0.2:
            cloned["timezone"] = random.choice(_TIMEZONES)
        cloned["canvas"] = _simple_hash(str(cloned.get("canvas", "")) + str(random.randint(0, 99999)))
        cloned["audio"] = _simple_hash(str(cloned.get("audio", "")) + str(random.randint(0, 50)))
    elif level == "high":
        if cloned.get("screen"):
            sw, sh = random.choice(_SCREEN_RESOLUTIONS)
            cloned["screen"]["width"] = sw
            cloned["screen"]["height"] = sh
        ua = str(cloned.get("userAgent", ""))
        if "Chrome/" in ua:
            version = int(ua.split("Chrome/")[1].split(".")[0])
            cloned["userAgent"] = ua.replace(f"Chrome/{version}", f"Chrome/{version + random.randint(2, 6)}")
        cloned["doNotTrack"] = "1" if random.random() < 0.3 else False
        if random.random() < 0.5:
            extras = [item for item in _FONT_POOL if item not in cloned.get("fonts", [])][: random.randint(1, 4)]
            cloned["fonts"] = list(cloned.get("fonts", [])) + extras
        else:
            fonts = list(cloned.get("fonts", []))
            target = max(4, len(fonts) - random.randint(1, 3))
            cloned["fonts"] = fonts[:target]
        cloned["canvas"] = _simple_hash(str(cloned.get("canvas", "")) + str(random.randint(0, 9999999)))
        cloned["webgl"] = _simple_hash(str(cloned.get("webgl", "")) + str(random.randint(0, 9999999)))
    elif level == "extreme":
        return create_base_fingerprint(random.randint(50000, 1000000))
    elif level == "none":
        return cloned
    else:
        raise ValueError(f"Unsupported mutation level: {level}")
    return cloned


def generate_dataset(size: int, sessions_per_device: int = 2) -> List[LabeledFingerprint]:
    records: List[LabeledFingerprint] = []
    mutation_cycle = ["none", "low", "medium", "high", "low"]

    for i in range(size):
        device_id = f"dev_{uuid4()}"
        is_attractor = random.random() < 0.125
        base = create_attractor_fingerprint(i) if is_attractor else create_base_fingerprint(i)

        for session_index in range(sessions_per_device):
            level = mutation_cycle[session_index % len(mutation_cycle)]
            payload = mutate(base, level)
            if level != "none" and random.random() < 0.4:
                payload = mutate(payload, "low")
            records.append(
                LabeledFingerprint(
                    id=device_id,
                    data=payload,
                    device_label=device_id,
                    is_attractor=is_attractor,
                )
            )

    return records
