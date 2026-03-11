from devicer.libs.comparators import jaccard_similarity, levenshtein_similarity, numeric_proximity, screen_similarity


def test_levenshtein_similarity_cases():
    assert levenshtein_similarity("abc", "abc") == 1
    assert levenshtein_similarity("", "abc") == 0
    assert levenshtein_similarity("", "") == 1
    score = levenshtein_similarity("kitten", "sitten")
    assert 0 < score < 1
    assert levenshtein_similarity("Mozilla/5.0", "Mozilla/5.1") > levenshtein_similarity("Mozilla/5.0", "Safari")


def test_jaccard_similarity_cases():
    assert jaccard_similarity(["a", "b"], ["a", "b"]) == 1
    assert jaccard_similarity([], []) == 1
    assert jaccard_similarity([], ["a"]) == 0
    assert jaccard_similarity(["a", "b", "c"], ["b", "c", "d"]) == 0.5
    assert jaccard_similarity(["x"], ["y"]) == 0
    assert jaccard_similarity(None, None) == 1


def test_numeric_proximity_cases():
    assert numeric_proximity(100, 100) == 1
    assert numeric_proximity(None, 100) == 0.5
    assert numeric_proximity(1920, 1900) > 0.9
    assert numeric_proximity(1, 1000) < 0.1
    assert numeric_proximity("win32", "win32") == 1
    assert numeric_proximity("win32", "linux") == 0


def test_screen_similarity_cases():
    base = {
        "width": 1920,
        "height": 1080,
        "colorDepth": 24,
        "pixelDepth": 24,
        "orientation": {"type": "landscape-primary", "angle": 0},
    }
    assert screen_similarity(base, base) == 1
    assert screen_similarity(None, base) == 0.5

    rotated = {**base, "orientation": {"type": "portrait-primary", "angle": 90}}
    assert round(screen_similarity(base, rotated), 1) == 0.8

    partial = {"width": 1920, "height": 1080}
    score = screen_similarity(base, partial)
    assert 0 < score <= 1
