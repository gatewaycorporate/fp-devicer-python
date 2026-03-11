import pytest

from devicer.libs.registry import (
    clear_registry,
    get_global_registry,
    register_comparator,
    register_plugin,
    register_weight,
    set_default_weight,
    unregister_comparator,
    unregister_weight,
)


def setup_function():
    clear_registry()


def test_register_comparator():
    fn = lambda a, b, _p=None: 1 if a == b else 0
    register_comparator("customField", fn)
    assert get_global_registry().comparators["customField"] is fn


def test_register_comparator_invalid():
    with pytest.raises(TypeError):
        register_comparator("field", None)


def test_register_weight_and_plugin():
    register_weight("fonts", 42)
    assert get_global_registry().weights["fonts"] == 42

    fn = lambda a, b, _p=None: 0.5
    register_plugin("customPlugin", weight=10, comparator=fn)
    reg = get_global_registry()
    assert reg.weights["customPlugin"] == 10
    assert reg.comparators["customPlugin"] is fn


def test_unregister_and_default_weight():
    register_weight("x", 7)
    register_comparator("x", lambda *_: 1)
    assert unregister_weight("x") is True
    assert unregister_comparator("x") is True

    set_default_weight(-1)
    assert get_global_registry().default_weight == 0


def test_clear_registry_resets_custom_values():
    register_weight("f", 10)
    clear_registry()
    reg = get_global_registry()
    assert "f" not in reg.weights
