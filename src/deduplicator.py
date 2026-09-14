"""
Deduplication system for identifying duplicate business records
"""

import logging
from typing import List, Dict, Optional, Tuple
from src.database import DatabaseManager
from src.normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class Deduplicator:
    """Identifies and manages duplicate business records"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize deduplicator

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def check_duplicate(self, business_data: Dict) -> Tuple[bool, Optional[int], str]:
        """
        Check if a business is a duplicate

        Args:
            business_data: Business data dictionary

        Returns:
            Tuple of (is_duplicate, duplicate_id, match_type)
        """
        # Priority 1: Exact website domain match
        if business_data.get('website'):
            normalized_website = DataNormalizer.normalize_website(business_data['website'])
            if normalized_website:
                existing = self.db_manager.get_business_by_website(normalized_website)
                if existing:
                    return (True, existing['id'], 'website_domain')

        # Priority 2: Exact phone match
        if business_data.get('phone'):
            normalized_phone = DataNormalizer.normalize_phone(business_data['phone'])
            if normalized_phone:
                existing = self.db_manager.get_business_by_phone(normalized_phone)
                if existing:
                    return (True, existing['id'], 'phone')

        # Priority 3: Exact normalized email match
        if business_data.get('email'):
            normalized_email = DataNormalizer.normalize_email(business_data['email'])
            if normalized_email:
                existing = self.db_manager.get_business_by_email(normalized_email)
                if existing:
                    return (True, existing['id'], 'email')

        # Priority 4: Business name + city match
        if business_data.get('business_name') and business_data.get('city'):
            normalized_name = DataNormalizer.normalize_business_name(business_data['business_name'])
            normalized_city = DataNormalizer.normalize_city(business_data['city'])

            if normalized_name and normalized_city:
                existing_id, existing = self._find_by_name_and_city(normalized_name, normalized_city)
                if existing_id:
                    # Verify with additional criteria to avoid false positives
                    if self._verify_name_city_match(business_data, existing):
                        return (True, existing_id, 'name_city')

        # Priority 5: Business name + address match
        if business_data.get('business_name') and business_data.get('address'):
            normalized_name = DataNormalizer.normalize_business_name(business_data['business_name'])
            normalized_address = DataNormalizer.normalize_address(business_data['address'])

            if normalized_name and normalized_address:
                existing_id, existing = self._find_by_name_and_address(normalized_name, normalized_address)
                if existing_id:
                    if self._verify_name_address_match(business_data, existing):
                        return (True, existing_id, 'name_address')

        return (False, None, 'none')

    def _find_by_name_and_city(self, name: str, city: str) -> tuple:
        """Find business by normalized name and city"""
        with self.db_manager.get_session() as session:
            from src.models import Business
            businesses = session.query(Business).filter(
                Business.city == city
            ).all()

            for business in businesses:
                # Convert to dict while session is active
                business_dict = business.to_dict()
                normalized_existing_name = DataNormalizer.normalize_business_name(business_dict['business_name'])
                if normalized_existing_name == name:
                    return (business.id, business_dict)

        return (None, None)

    def _find_by_name_and_address(self, name: str, address: str) -> tuple:
        """Find business by normalized name and address"""
        with self.db_manager.get_session() as session:
            from src.models import Business
            businesses = session.query(Business).filter(
                Business.address == address
            ).all()

            for business in businesses:
                # Convert to dict while session is active
                business_dict = business.to_dict()
                normalized_existing_name = DataNormalizer.normalize_business_name(business_dict['business_name'])
                if normalized_existing_name == name:
                    return (business.id, business_dict)

        return (None, None)

    def _verify_name_city_match(self, new_data: Dict, existing: Dict) -> bool:
        """
        Verify that name+city match is likely a true duplicate

        Args:
            new_data: New business data
            existing: Existing business record (dictionary)

        Returns:
            bool: True if likely duplicate
        """
        # Check if other fields match
        matches = 0

        # Check country
        if new_data.get('country') == existing.get('country'):
            matches += 1

        # Check category
        if new_data.get('category') and existing.get('category'):
            if new_data['category'].lower() == existing['category'].lower():
                matches += 1

        # Check phone
        if new_data.get('phone') and existing.get('phone'):
            new_phone = DataNormalizer.normalize_phone(new_data['phone'])
            existing_phone = DataNormalizer.normalize_phone(existing['phone'])
            if new_phone == existing_phone:
                matches += 1

        # If at least 2 additional fields match, consider it a duplicate
        return matches >= 2

    def _verify_name_address_match(self, new_data: Dict, existing: Dict) -> bool:
        """
        Verify that name+address match is likely a true duplicate

        Args:
            new_data: New business data
            existing: Existing business record (dictionary)

        Returns:
            bool: True if likely duplicate
        """
        # Check country
        if new_data.get('country') != existing.get('country'):
            return False

        # Check city
        if new_data.get('city') and existing.get('city'):
            new_city = DataNormalizer.normalize_city(new_data['city'])
            existing_city = DataNormalizer.normalize_city(existing['city'])
            if new_city != existing_city:
                return False

        return True

    def mark_duplicate(self, business_id: int, duplicate_of: int, match_type: str):
        """
        Mark a business as a duplicate

        Args:
            business_id: ID of business to mark
            duplicate_of: ID of original business
            match_type: Type of match (website_domain, phone, email, etc.)
        """
        update_data = {
            'duplicate': 'true',
            'duplicate_of': duplicate_of,
            'verification_notes': f'Marked as duplicate via {match_type} match'
        }
        self.db_manager.update_business(business_id, update_data)
        logger.info(f"Marked business {business_id} as duplicate of {duplicate_of} ({match_type})")

    def mark_possible_duplicate(self, business_id: int, reason: str):
        """
        Mark a business as a possible duplicate

        Args:
            business_id: ID of business to mark
            reason: Reason for possible duplicate
        """
        update_data = {
            'duplicate': 'possible',
            'verification_notes': f'Possible duplicate: {reason}'
        }
        self.db_manager.update_business(business_id, update_data)
        logger.info(f"Marked business {business_id} as possible duplicate: {reason}")

    def run_deduplication(self) -> Dict:
        """
        Run deduplication on all businesses in database

        Returns:
            Dictionary with deduplication statistics
        """
        logger.info("Starting deduplication process")

        stats = {
            'total_checked': 0,
            'duplicates_found': 0,
            'possible_duplicates': 0,
            'unique_remaining': 0
        }

        # Get all non-duplicate businesses (now returns dictionaries)
        businesses = self.db_manager.get_all_businesses()
        businesses = [b for b in businesses if b.get('duplicate') != 'true']

        stats['total_checked'] = len(businesses)

        for business_data in businesses:
            is_duplicate, duplicate_id, match_type = self.check_duplicate(business_data)

            if is_duplicate and duplicate_id:
                self.mark_duplicate(business_data['id'], duplicate_id, match_type)
                stats['duplicates_found'] += 1
            elif is_duplicate and not duplicate_id:
                # Mark as possible if we can't find the original
                self.mark_possible_duplicate(business_data['id'], match_type)
                stats['possible_duplicates'] += 1

        stats['unique_remaining'] = stats['total_checked'] - stats['duplicates_found']

        logger.info(f"Deduplication complete: {stats['duplicates_found']} duplicates, "
                   f"{stats['possible_duplicates']} possible duplicates")

        return stats
