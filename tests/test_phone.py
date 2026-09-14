"""
Tests for phone validation
"""

import unittest
from src.normalizer import DataNormalizer


class TestPhoneValidation(unittest.TestCase):
    """Test cases for phone validation"""

    def test_valid_phones(self):
        """Test valid phone numbers"""
        valid_phones = [
            '+1-555-123-4567',
            '(555) 123-4567',
            '555.123.4567',
            '555 123 4567',
            '+971 50 123 4567',
            '0044 20 1234 5678',
        ]

        for phone in valid_phones:
            normalized = DataNormalizer.normalize_phone(phone)
            self.assertIsNotNone(normalized, f"Failed to normalize valid phone: {phone}")
            self.assertGreaterEqual(len(normalized), 7)

    def test_invalid_phones(self):
        """Test invalid phone numbers"""
        invalid_phones = [
            '123',  # Too short
            '',
            None,
            'abc',
        ]

        for phone in invalid_phones:
            normalized = DataNormalizer.normalize_phone(phone)
            self.assertIsNone(normalized, f"Should reject invalid phone: {phone}")

    def test_phone_normalization(self):
        """Test phone normalization (remove formatting)"""
        test_cases = [
            ('+1-555-123-4567', '15551234567'),
            ('(555) 123-4567', '5551234567'),
            ('555.123.4567', '5551234567'),
            ('+971 50 123 4567', '971501234567'),
            ('0044 20 1234 5678', '442012345678'),
        ]

        for input_phone, expected in test_cases:
            normalized = DataNormalizer.normalize_phone(input_phone)
            self.assertEqual(normalized, expected)

    def test_international_phones(self):
        """Test international phone numbers"""
        test_cases = [
            ('+971 50 123 4567', '971501234567'),  # UAE
            ('+1 202 555 0123', '12025550123'),    # USA
            ('+44 20 7946 0958', '442079460958'),  # UK
        ]

        for input_phone, expected in test_cases:
            normalized = DataNormalizer.normalize_phone(input_phone)
            self.assertEqual(normalized, expected)

    def test_phone_with_extensions(self):
        """Test phone numbers with extensions"""
        # Extensions should be preserved in the number
        phone = '555-123-4567 ext 123'
        normalized = DataNormalizer.normalize_phone(phone)
        # The extension digits would be included since we only remove non-numeric except +
        self.assertIsNotNone(normalized)


if __name__ == '__main__':
    unittest.main()
