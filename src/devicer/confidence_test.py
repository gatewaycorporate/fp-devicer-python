import unittest
from confidence import calculate_confidence
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


class TestConfidenceCalculation(unittest.TestCase):
    def test_confidence_range(self):
        """
        Test that the confidence score is between 0 and 100.
        """
        confidence = calculate_confidence(sampleData1, sampleData2)
        self.assertGreaterEqual(confidence, 0, "Confidence score should be at least 0.")
        self.assertLessEqual(confidence, 100, "Confidence score should not exceed 100.")

    def test_confidence_identical_data(self):
        """
        Test that the confidence score is 100 when both data dictionaries are identical.
        """
        confidence = calculate_confidence(sampleData1, sampleData1)
        self.assertEqual(confidence, 100, "Confidence score should be 100 for identical data.")
    
    def test_confidence_different_data(self):
        """
        Test that the confidence score is less than 10 when data dictionaries are different.
        """
        confidence = calculate_confidence(sampleData1, sampleData2)
        self.assertLess(confidence, 10, "Confidence score should be less than 10 for different data.")

    def test_confidence_similar_data(self):
        """
        Test that the confidence score is greater than 80 when data dictionaries are similar.
        """
        similar_data = sampleData2.copy()
        similar_data['hardware']['ram'] = 8192
        confidence = calculate_confidence(sampleData2, similar_data)
        self.assertGreater(confidence, 80, "Confidence score should be greater than 80 for similar data.")

    def test_confidence_partial_data(self):
        """
        Test that the confidence score is calculated correctly when some fields match.
        """
        partial_data = sampleData1.copy()
        partial_data['hardware']['cpu'] = 'Pentium 4'
        partial_data['hardware']['gpu'] = 'Intel HD Graphics'
        partial_data['hardware']['ram'] = 4096
        partial_data['timezone'] = 'Europe/London'
        partial_data['ip'] = '178.238.11.6'
        partial_data['languages'] = ['en-GB', 'en']
        partial_data['userAgent'] = 'Mozilla/5.0 (compatible; Konqueror/2.2.2-3; Linux)'
        confidence = calculate_confidence(sampleData1, partial_data)
        self.assertGreater(confidence, 10, "Confidence score should be greater than 10 for partially matching data.")
        self.assertLess(confidence, 95, "Confidence score should be less than 95 for partially matching data.")

    def test_confidence_empty_data(self):
        """
        Test that the confidence score is 0 when one of the data dictionaries is empty.
        """
        confidence = calculate_confidence({}, sampleData2)
        self.assertEqual(confidence, 0, "Confidence score should be 0 for empty data.")
        
        confidence = calculate_confidence(sampleData1, {})
        self.assertEqual(confidence, 0, "Confidence score should be 0 for empty data.")
        
        confidence = calculate_confidence({}, {})
        self.assertEqual(confidence, 0, "Confidence score should be 0 for both data dictionaries being empty.")

if __name__ == '__main__':
    unittest.main()