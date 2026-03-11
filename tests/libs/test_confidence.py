from devicer.libs.confidence import calculate_confidence, create_confidence_calculator
from devicer.libs.default_plugins import initialize_default_registry
from devicer.libs.registry import clear_registry
from devicer.types import ComparisonOptions
from tests.fixtures.fingerprints import (
    fp_different,
    fp_identical,
    fp_similar,
    fp_very_different,
    fp_very_similar,
)


def test_confidence_basic_ranges():
    score = calculate_confidence(fp_identical, fp_very_similar)
    assert isinstance(score, int)
    assert 0 <= score <= 100


def test_confidence_expected_ordering():
    same = calculate_confidence(fp_identical, fp_identical)
    very_sim = calculate_confidence(fp_identical, fp_very_similar)
    sim = calculate_confidence(fp_identical, fp_similar)
    diff = calculate_confidence(fp_identical, fp_different)
    very_diff = calculate_confidence(fp_identical, fp_very_different)

    assert same == 100
    assert very_sim >= sim >= diff >= very_diff


def test_confidence_handles_incomplete_data():
    incomplete = {**fp_identical, "plugins": [], "screen": None}
    score = calculate_confidence(fp_identical, incomplete)
    assert 0 < score < 100


def test_confidence_calculator_options():
    clear_registry()
    initialize_default_registry()

    structural = create_confidence_calculator(user_options=ComparisonOptions(tlsh_weight=0))
    tls_only = create_confidence_calculator(user_options=ComparisonOptions(tlsh_weight=1))

    assert structural.calculate_confidence(fp_identical, fp_identical) == 100
    assert tls_only.calculate_confidence(fp_identical, fp_identical) == 100

    close_struct = structural.calculate_confidence(fp_identical, fp_very_similar)
    far_struct = structural.calculate_confidence(fp_identical, fp_very_different)
    assert close_struct > far_struct


def test_custom_weight_override_changes_score_when_canvas_zeroed():
    clear_registry()
    initialize_default_registry()

    fp_canvas_diff = {**fp_identical, "canvas": "completely_different_canvas_hash"}
    zero_canvas = create_confidence_calculator(user_options=ComparisonOptions(weights={"canvas": 0}, tlsh_weight=0))
    default_calc = create_confidence_calculator(user_options=ComparisonOptions(tlsh_weight=0))

    score_zero_canvas = zero_canvas.calculate_confidence(fp_identical, fp_canvas_diff)
    score_default = default_calc.calculate_confidence(fp_identical, fp_canvas_diff)
    assert score_zero_canvas > score_default
