import re

from devicer.benchmarks.data_generator import (
    create_attractor_fingerprint,
    create_base_fingerprint,
    generate_dataset,
    mutate,
)


def test_generate_fingerprints_browser_diversity():
    dataset = generate_dataset(50, 2)
    vendors = {entry.data.get("vendor") for entry in dataset}
    assert len(vendors) > 1


def test_generate_realistic_canvas_webgl_audio_blobs():
    fp = create_base_fingerprint(123)
    assert re.match(r"^[0-9a-z]+$", fp["canvas"])
    assert re.match(r"^[0-9a-z]+$", fp["webgl"])
    assert re.match(r"^[0-9a-z]+$", fp["audio"])
    assert len(fp["canvas"]) >= 4
    assert len(fp["webgl"]) >= 4
    assert len(fp["audio"]) >= 4


def test_generate_attractor_zone_devices():
    attractor = create_attractor_fingerprint(1)
    assert attractor["platform"] == "Win32"
    assert attractor["language"] == "en-US"
    assert attractor["timezone"] == "America/New_York"
    assert attractor["hardwareConcurrency"] == 8
    assert attractor["deviceMemory"] == 8

    dataset = generate_dataset(200, 1)
    attractors = [entry for entry in dataset if entry.is_attractor]
    assert len(attractors) > 0
    for entry in attractors:
        assert entry.data["platform"] == "Win32"
        assert entry.data["language"] == "en-US"
        assert entry.data["timezone"] == "America/New_York"
        assert entry.data["hardwareConcurrency"] == 8
        assert entry.data["deviceMemory"] == 8


def test_mutate_fingerprints_realistically():
    fp = create_base_fingerprint(42)
    assert mutate(fp, "none") == fp
    assert mutate(fp, "low") != fp
    assert mutate(fp, "medium") != fp
    assert mutate(fp, "high") != fp
    assert mutate(fp, "extreme") != fp
