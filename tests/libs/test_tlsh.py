import random
import string

import pytest

from devicer.libs.hashing import compare_hashes, get_hash


def random_string(length: int) -> str:
    chars = string.ascii_letters + string.digits + "[]{};!@#$%^&*()-_=+|;:\",.<>?"
    return "".join(random.choice(chars) for _ in range(length))


def test_hash_non_empty_for_large_string():
    value = random_string(524)
    assert isinstance(get_hash(value), str)
    assert len(get_hash(value)) > 0


def test_hash_deterministic():
    value = random_string(524)
    assert get_hash(value) == get_hash(value)


def test_compare_identical_hashes_zero_distance():
    value = random_string(524)
    h1 = get_hash(value)
    h2 = get_hash(value)
    assert compare_hashes(h1, h2) == 0


def test_compare_different_hashes_non_negative():
    h1 = get_hash(random_string(524))
    h2 = get_hash(random_string(524))
    assert compare_hashes(h1, h2) >= 0


def test_similar_hashes_smallish_distance():
    value = random_string(524)
    idx = random.randint(0, len(value) - 5)
    modified = value[:idx] + random_string(4) + value[idx + 4 :]
    distance = compare_hashes(get_hash(value), get_hash(modified))
    assert distance > 0
    assert distance < 200


def test_invalid_hash_handling():
    assert compare_hashes("invalidhash", "anotherinvalid") >= 0
