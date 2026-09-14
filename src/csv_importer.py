"""
CSV importer for authorized/user-provided business data
"""

import csv
import logging
from typing import List, Dict, Optional
from pathlib import Path
from src.normalizer import DataNormalizer
from src.database import DatabaseManager

logger = logging.getLogger(__name__)


class CSVImporter:
    """Imports business data from CSV files"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize CSV importer

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def import_csv(self, csv_path: str, source_name: str = "CSV Import") -> Dict:
        """
        Import businesses from CSV file

        Args:
            csv_path: Path to CSV file
            source_name: Name to use as source

        Returns:
            Dictionary with import statistics
        """
        logger.info(f"Starting CSV import from {csv_path}")

        stats = {
            'total_rows': 0,
            'imported': 0,
            'skipped': 0,
            'errors': 0,
            'duplicates': 0
        }

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    stats['total_rows'] += 1

                    try:
                        business_data = self._parse_row(row, source_name)

                        if not business_data:
                            stats['skipped'] += 1
                            continue

                        # Check for duplicates
                        from src.deduplicator import Deduplicator
                        deduplicator = Deduplicator(self.db_manager)
                        is_duplicate, duplicate_id, match_type = deduplicator.check_duplicate(business_data)

                        if is_duplicate:
                            stats['duplicates'] += 1
                            logger.info(f"Skipping duplicate: {business_data.get('business_name')} ({match_type})")
                            continue

                        # Add to database
                        self.db_manager.add_business(business_data)
                        stats['imported'] += 1

                        logger.debug(f"Imported: {business_data.get('business_name')}")

                    except Exception as e:
                        stats['errors'] += 1
                        logger.error(f"Error importing row {stats['total_rows']}: {e}")

            logger.info(f"CSV import complete: {stats['imported']} imported, "
                       f"{stats['duplicates']} duplicates, {stats['skipped']} skipped, "
                       f"{stats['errors']} errors")

            return stats

        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            raise

    def _parse_row(self, row: Dict, source_name: str) -> Optional[Dict]:
        """
        Parse a CSV row into business data

        Args:
            row: CSV row dictionary
            source_name: Source name to use

        Returns:
            Business data dictionary or None
        """
        # Extract fields with flexible column names
        business_name = self._get_value(row, ['name', 'business_name', 'company', 'title'])
        if not business_name:
            logger.warning("Row missing business name, skipping")
            return None

        business_data = {
            'business_name': business_name.strip(),
            'category': self._get_value(row, ['category', 'industry', 'type']),
            'subcategory': self._get_value(row, ['subcategory']),
            'country': self._get_value(row, ['country'], default='Unknown'),
            'state': self._get_value(row, ['state', 'province', 'region']),
            'city': self._get_value(row, ['city', 'town', 'locality']),
            'address': self._get_value(row, ['address', 'location', 'street']),
            'postal_code': self._get_value(row, ['postal_code', 'zip', 'postcode']),
            'phone': self._normalize_phone(self._get_value(row, ['phone', 'telephone', 'tel'])),
            'email': self._normalize_email(self._get_value(row, ['email', 'email_address'])),
            'website': self._normalize_website(self._get_value(row, ['website', 'url', 'site'])),
            'rating': self._parse_float(self._get_value(row, ['rating', 'stars'])),
            'review_count': self._parse_int(self._get_value(row, ['review_count', 'reviews'])),
            'source': source_name,
            'source_url': self._get_value(row, ['source_url', 'url'], default='CSV Import'),
            'source_type': 'csv',
            'source_verified': True,
            'verification_status': 'PENDING',
            'directory_email': self._normalize_email(self._get_value(row, ['email', 'email_address'])),
            'directory_phone': self._normalize_phone(self._get_value(row, ['phone', 'telephone', 'tel'])),
        }

        # Remove None values
        business_data = {k: v for k, v in business_data.items() if v is not None}

        return business_data

    def _get_value(self, row: Dict, keys: List[str], default: str = None) -> Optional[str]:
        """
        Get value from row using multiple possible keys

        Args:
            row: CSV row dictionary
            keys: List of possible keys to try
            default: Default value if none found

        Returns:
            Value or default
        """
        for key in keys:
            if key in row and row[key]:
                value = row[key].strip()
                if value:
                    return value
        return default

    def _normalize_phone(self, phone: Optional[str]) -> Optional[str]:
        """Normalize phone number"""
        return DataNormalizer.normalize_phone(phone)

    def _normalize_email(self, email: Optional[str]) -> Optional[str]:
        """Normalize email address"""
        return DataNormalizer.normalize_email(email)

    def _normalize_website(self, website: Optional[str]) -> Optional[str]:
        """Normalize website URL"""
        return DataNormalizer.normalize_website(website)

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Parse float value"""
        if not value:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Parse integer value"""
        if not value:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def validate_csv_structure(self, csv_path: str) -> bool:
        """
        Validate CSV file structure

        Args:
            csv_path: Path to CSV file

        Returns:
            bool: True if valid structure
        """
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                # Check if file has at least one row
                if not reader.fieldnames:
                    logger.error("CSV file has no headers")
                    return False

                # Check for at least one identifying field
                required_fields = ['name', 'business_name', 'company', 'title']
                has_required = any(field in reader.fieldnames for field in required_fields)

                if not has_required:
                    logger.error("CSV file missing required field (name/business_name/company/title)")
                    return False

                return True

        except Exception as e:
            logger.error(f"Error validating CSV structure: {e}")
            return False
