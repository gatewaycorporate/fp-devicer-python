import unittest
import random
from hashing import get_tlsh_hash, get_hash_difference
from hashing_test import random_string

sampleData1 = {
  "fonts": ['Arial', 'Verdana'],
  "hardware": {
    "cpu": 'Intel Core i7',
    "gpu": 'NVIDIA GTX 1080',
    "ram": 16384
  },
  "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
  "screen": {
    "width": 1920,
    "height": 1080,
    "colorDepth": 24
  },
  "timezone": 'America/New_York',
  "ip": '157.185.170.244',
  "languages": ['en-US', 'en'],
  "plugins": ['Chrome PDF Viewer', 'Shockwave Flash'],
  "canvasHash": random_string().encode('utf-8'),
  "audioHash": random_string().encode('utf-8'),
  "webglHash": random_string().encode('utf-8'),
}

sampleData2 = {
  "fonts": ['Arial', 'Verdana'],
  "hardware": {
    "cpu": 'Pentium 4',
    "gpu": 'Intel HD Graphics',
    "ram": 4096
  },
  "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
  "screen": {
    "width": 1280,
    "height": 720,
    "colorDepth": 24
  },
  "timezone": 'Europe/London',
  "ip": '178.238.11.6',
  "languages": ['en-GB', 'en'],
  "plugins": ['Chrome PDF Viewer', 'Shockwave Flash'],
  "canvasHash": random_string().encode('utf-8'),
  "audioHash": random_string().encode('utf-8'),
  "webglHash": random_string().encode('utf-8'),
}


class TestHashingData(unittest.TestCase):
    def test_hash_nonempty(self):
        """
        Test that the hashing function returns a non-empty string for a non-empty input.
        """
        data = str(sampleData1).encode('utf-8')
        hash_value = get_tlsh_hash(data)
        self.assertTrue(hash_value, "Hash value should not be empty for non-empty input.")

    def test_hash_identical_inputs(self):
        """
        Test that the hashing function returns the same hash for identical inputs.
        Also checks that the difference between the hashes is zero.
        """
        data = str(sampleData1).encode('utf-8')
        hash1 = get_tlsh_hash(data)
        hash2 = get_tlsh_hash(data)
        difference = get_hash_difference(hash1, hash2)
        self.assertEqual(hash1, hash2, "Hash values should be identical for identical inputs.")
        self.assertEqual(difference, 0, "Hash difference should be zero for identical inputs.")
      
    def test_hash_distance_when_different(self):
        """
        Test that the hash difference is non-zero for different inputs.
        Also checks that the difference is large for sufficiently different inputs.
        """
        data1 = str(sampleData1).encode('utf-8')
        data2 = str(sampleData2).encode('utf-8')
        hash1 = get_tlsh_hash(data1)
        hash2 = get_tlsh_hash(data2)
        difference = get_hash_difference(hash1, hash2)
        self.assertGreater(difference, 0, "Hash difference should be greater than zero for different inputs.")
        self.assertGreater(difference, 80, "Hash difference should be large for sufficiently different inputs.")

    def test_hash_distance_when_similar(self):
        """
        Test that the hash difference is small for similar inputs.
        """
        data1 = str(sampleData1).encode('utf-8')
        random_index = random.randint(0, len(data1) - 4)
        data2 = data1[:random_index] + random_string(length=4).encode('utf-8') + data1[random_index + 4:]
        hash1 = get_tlsh_hash(data1)
        hash2 = get_tlsh_hash(data2)
        difference = get_hash_difference(hash1, hash2)
        self.assertLess(difference, 140, "Hash difference should be small for similar inputs.")

if __name__ == '__main__':
    unittest.main()