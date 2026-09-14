"""
Tests for deduplicator
"""

import unittest
import tempfile
import os
from src.database import DatabaseManager
from src.deduplicator import Deduplicator
from src.models import Business


class TestDeduplicator(unittest.TestCase):
    """Test cases for Deduplicator"""

    def setUp(self):
        """Set up test database"""
        self.db_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.db_file.name
        self.db_file.close()

        self.db_manager = DatabaseManager(self.db_path)
        self.deduplicator = Deduplicator(self.db_manager)

    def tearDown(self):
        """Clean up test database"""
        self.db_manager.engine.dispose()
        os.unlink(self.db_path)

    def test_check_duplicate_by_website(self):
        """Test duplicate detection by website"""
        # Add first business with normalized website
        from src.normalizer import DataNormalizer
        normalized_website = DataNormalizer.normalize_website('https://example.com')

        business1 = {
            'business_name': 'Test Company',
            'website': normalized_website,  # Store normalized website
            'country': 'USA',
            'source': 'Test',
            'source_url': 'https://test.com',
            'source_type': 'directory',
            'source_verified': True,
            'verification_status': 'PENDING'
        }
        self.db_manager.add_business(business1)

        # Check duplicate with same normalized website
        business2 = {
            'business_name': 'Test Company LLC',
            'website': normalized_website,  # Same normalized website
            'country': 'USA'
        }
        is_duplicate, duplicate_id, match_type = self.deduplicator.check_duplicate(business2)

        self.assertTrue(is_duplicate)
        self.assertEqual(match_type, 'website_domain')

    def test_check_duplicate_by_phone(self):
        """Test duplicate detection by phone"""
        # Add first business with normalized phone
        from src.normalizer import DataNormalizer
        normalized_phone = DataNormalizer.normalize_phone('+1-555-123-4567')

        business1 = {
            'business_name': 'Test Company',
            'phone': normalized_phone,  # Store normalized phone
            'country': 'USA',
            'source': 'Test',
            'source_url': 'https://test.com',
            'source_type': 'directory',
            'source_verified': True,
            'verification_status': 'PENDING'
        }
        self.db_manager.add_business(business1)

        # Check duplicate with same normalized phone
        business2 = {
            'business_name': 'Test Company LLC',
            'phone': normalized_phone,  # Same normalized phone
            'country': 'USA'
        }
        is_duplicate, duplicate_id, match_type = self.deduplicator.check_duplicate(business2)

        self.assertTrue(is_duplicate)
        self.assertEqual(match_type, 'phone')

    def test_check_duplicate_by_email(self):
        """Test duplicate detection by email"""
        # Add first business with normalized email
        from src.normalizer import DataNormalizer
        normalized_email = DataNormalizer.normalize_email('info@example.com')

        business1 = {
            'business_name': 'Test Company',
            'email': normalized_email,  # Store normalized email
            'country': 'USA',
            'source': 'Test',
            'source_url': 'https://test.com',
            'source_type': 'directory',
            'source_verified': True,
            'verification_status': 'PENDING'
        }
        self.db_manager.add_business(business1)

        # Check duplicate with same normalized email
        business2 = {
            'business_name': 'Test Company LLC',
            'email': normalized_email,  # Same normalized email
            'country': 'USA'
        }
        is_duplicate, duplicate_id, match_type = self.deduplicator.check_duplicate(business2)

        self.assertTrue(is_duplicate)
        self.assertEqual(match_type, 'email')

    def test_no_duplicate(self):
        """Test when no duplicate exists"""
        # Add first business
        business1 = {
            'business_name': 'Test Company',
            'country': 'USA',
            'source': 'Test',
            'source_url': 'https://test.com',
            'source_type': 'directory',
            'source_verified': True,
            'verification_status': 'PENDING'
        }
        self.db_manager.add_business(business1)

        # Check duplicate with different business
        business2 = {
            'business_name': 'Different Company',
            'country': 'USA'
        }
        is_duplicate, duplicate_id, match_type = self.deduplicator.check_duplicate(business2)

        self.assertFalse(is_duplicate)
        self.assertIsNone(duplicate_id)
        self.assertEqual(match_type, 'none')


if __name__ == '__main__':
    unittest.main()
