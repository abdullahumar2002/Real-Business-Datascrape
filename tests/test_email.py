"""
Tests for email validation
"""

import unittest
from src.normalizer import DataNormalizer


class TestEmailValidation(unittest.TestCase):
    """Test cases for email validation"""

    def test_valid_emails(self):
        """Test valid email addresses"""
        valid_emails = [
            'test@example.com',
            'user.name@example.com',
            'user+tag@example.com',
            'user@sub.example.com',
            'TEST@EXAMPLE.COM',
        ]

        for email in valid_emails:
            normalized = DataNormalizer.normalize_email(email)
            self.assertIsNotNone(normalized, f"Failed to normalize valid email: {email}")
            self.assertEqual(normalized, email.lower())

    def test_invalid_emails(self):
        """Test invalid email addresses"""
        invalid_emails = [
            'invalid',
            '@example.com',
            'user@',
            '',
            None,
        ]

        for email in invalid_emails:
            normalized = DataNormalizer.normalize_email(email)
            self.assertIsNone(normalized, f"Should reject invalid email: {email}")

    def test_email_normalization(self):
        """Test email normalization (lowercase, trim)"""
        test_cases = [
            ('  Test@Example.COM  ', 'test@example.com'),
            ('USER@DOMAIN.COM', 'user@domain.com'),
            ('First.Last@Example.Com', 'first.last@example.com'),
        ]

        for input_email, expected in test_cases:
            normalized = DataNormalizer.normalize_email(input_email)
            self.assertEqual(normalized, expected)

    def test_email_with_whitespace(self):
        """Test email with whitespace"""
        email = '  test@example.com  '
        normalized = DataNormalizer.normalize_email(email)
        self.assertEqual(normalized, 'test@example.com')


if __name__ == '__main__':
    unittest.main()
