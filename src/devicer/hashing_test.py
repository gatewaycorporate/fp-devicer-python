import unittest
import random
from hashing import get_tlsh_hash, get_hash_difference

def random_string(length=524):
    """
    Generate a random string of specified length.

    Args:
        length (int): The length of the string to generate. Default is 524.

    Returns:
        str: A random string of the specified length.
    """
    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789[];!@#$%^&*()-_=+|;:,.<>?"
    return ''.join(random.choice(characters) for _ in range(length))


class TestHashingMethods(unittest.TestCase):
    def test_hash_nonempty(self):
        """
        Test that the hashing function returns a non-empty string for a non-empty input.
        """
        data = random_string()
        hash_value = get_tlsh_hash(data.encode('utf-8'))
        self.assertTrue(hash_value, "Hash value should not be empty for non-empty input.")

    def test_hash_identical_inputs(self):
        """
        Test that the hashing function returns the same hash for identical inputs.
        Also checks that the difference between the hashes is zero.
        """
        data = random_string()
        hash1 = get_tlsh_hash(data.encode('utf-8'))
        hash2 = get_tlsh_hash(data.encode('utf-8'))
        difference = get_hash_difference(hash1, hash2)
        self.assertEqual(hash1, hash2, "Hash values should be identical for identical inputs.")
        self.assertEqual(difference, 0, "Hash difference should be zero for identical inputs.")

    def test_hash_distance_when_different(self):
        """
        Test that the hash difference is non-zero for different inputs.
        Also checks that the difference is large for sufficiently different inputs.
        """
        data1 = random_string()
        data2 = random_string()
        hash1 = get_tlsh_hash(data1.encode('utf-8'))
        hash2 = get_tlsh_hash(data2.encode('utf-8'))
        difference = get_hash_difference(hash1, hash2)
        self.assertGreater(difference, 0, "Hash difference should be greater than zero for different inputs.")
        self.assertGreater(difference, 180, "Hash difference should be large for sufficiently different inputs.")

    def test_hash_distance_when_similar(self):
        """
        Test that the hash difference is small for similar inputs.
        """
        data1 = random_string()
        random_index = random.randint(0, len(data1) - 4)
        data2 = data1[:random_index] + random_string(length=4) + data1[random_index + 4:]
        hash1 = get_tlsh_hash(data1.encode('utf-8'))
        hash2 = get_tlsh_hash(data2.encode('utf-8'))
        difference = get_hash_difference(hash1, hash2)
        self.assertLess(difference, 200, "Hash difference should be small for similar inputs.")

if __name__ == '__main__':
    unittest.main()