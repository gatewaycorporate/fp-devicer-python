import copy

from devicer.benchmarks.data_generator import create_base_fingerprint

fp_identical = create_base_fingerprint(1)


def _clone(data):
	return copy.deepcopy(data)


fp_very_similar = _clone(fp_identical)
if fp_very_similar.get("screen"):
	fp_very_similar["screen"]["width"] = int(fp_very_similar["screen"]["width"]) + 1
fp_very_similar["canvas"] = f"{fp_very_similar.get('canvas', '')}a"


fp_similar = _clone(fp_identical)
fp_similar["timezone"] = "Europe/London"
if fp_similar.get("fonts"):
	fp_similar["fonts"] = list(fp_similar["fonts"][:-1])
fp_similar["audio"] = f"{fp_similar.get('audio', '')}b"
ua = str(fp_similar.get("userAgent", ""))
if "Chrome/" in ua:
	version = int(ua.split("Chrome/")[1].split(".")[0])
	fp_similar["userAgent"] = ua.replace(f"Chrome/{version}", f"Chrome/{version + 1}")


fp_different = _clone(fp_identical)
fp_different["platform"] = "Linux x86_64" if fp_identical.get("platform") != "Linux x86_64" else "Win32"
fp_different["language"] = "de-DE"
fp_different["languages"] = ["de-DE", "de", "en"]
fp_different["doNotTrack"] = "1"
if fp_different.get("screen"):
	fp_different["screen"]["width"] = 1366
	fp_different["screen"]["height"] = 768
fp_different["canvas"] = "different_canvas_fingerprint"
fp_different["webgl"] = "different_webgl_fingerprint"
fp_different["audio"] = "different_audio_fingerprint"


fp_very_different = create_base_fingerprint(99991)
