"""
Tests for data normalizer
"""

import unittest
from src.normalizer import DataNormalizer


class TestDataNormalizer(unittest.TestCase):
    """Test cases for DataNormalizer"""

    def test_normalize_phone(self):
        """Test phone number normalization"""
        # Test various phone formats
        self.assertEqual(DataNormalizer.normalize_phone("+971 50 123 4567"), "971501234567")
        self.assertEqual(DataNormalizer.normalize_phone("(555) 123-4567"), "5551234567")
        self.assertEqual(DataNormalizer.normalize_phone("555.123.4567"), "5551234567")
        self.assertEqual(DataNormalizer.normalize_phone("0044 20 1234 5678"), "442012345678")
        self.assertIsNone(DataNormalizer.normalize_phone("123"))  # Too short
        self.assertIsNone(DataNormalizer.normalize_phone(None))

    def test_normalize_email(self):
        """Test email normalization"""
        self.assertEqual(DataNormalizer.normalize_email("Test@Example.COM"), "test@example.com")
        self.assertEqual(DataNormalizer.normalize_email("  test@example.com  "), "test@example.com")
        self.assertIsNone(DataNormalizer.normalize_email("invalid-email"))
        self.assertIsNone(DataNormalizer.normalize_email(None))

    def test_normalize_business_name(self):
        """Test business name normalization"""
        # Now Company is not removed (it's too generic), only legal entity suffixes
        self.assertEqual(DataNormalizer.normalize_business_name("ABC Company LLC"), "Abc Company")
        self.assertEqual(DataNormalizer.normalize_business_name("XYZ Inc."), "Xyz")
        self.assertEqual(DataNormalizer.normalize_business_name("Test Ltd."), "Test")
        self.assertEqual(DataNormalizer.normalize_business_name("  test  "), "Test")
        self.assertIsNone(DataNormalizer.normalize_business_name(None))

    def test_normalize_website(self):
        """Test website normalization"""
        self.assertEqual(DataNormalizer.normalize_website("example.com"), "https://example.com")
        self.assertEqual(DataNormalizer.normalize_website("http://example.com"), "http://example.com")
        self.assertEqual(DataNormalizer.normalize_website("https://EXAMPLE.COM"), "https://example.com")
        self.assertIsNone(DataNormalizer.normalize_website(None))

    def test_extract_domain(self):
        """Test domain extraction"""
        self.assertEqual(DataNormalizer.extract_domain("https://example.com/path"), "example.com")
        self.assertEqual(DataNormalizer.extract_domain("http://sub.example.com"), "sub.example.com")
        self.assertIsNone(DataNormalizer.extract_domain(None))

    def test_are_similar_names(self):
        """Test name similarity checking"""
        self.assertTrue(DataNormalizer.are_similar_names("ABC Company LLC", "ABC Company"))
        self.assertTrue(DataNormalizer.are_similar_names("ABC Engineering", "ABC Engineering LLC"))
        self.assertFalse(DataNormalizer.are_similar_names("ABC Company", "XYZ Company"))
        self.assertFalse(DataNormalizer.are_similar_names("ABC", "XYZ"))


if __name__ == '__main__':
    unittest.main()
