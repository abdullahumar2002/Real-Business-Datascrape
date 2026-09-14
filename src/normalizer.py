"""
Data normalizer for standardizing business information
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalizes business data for consistency and deduplication"""

    @staticmethod
    def normalize_phone(phone: Optional[str]) -> Optional[str]:
        """
        Normalize phone number to standard format

        Args:
            phone: Phone number string

        Returns:
            Normalized phone number or None
        """
        if not phone:
            return None

        # Remove all non-numeric characters except +
        phone = re.sub(r'[^\d+]', '', phone)

        # Remove leading + if present (we'll add it back if needed)
        if phone.startswith('+'):
            phone = phone[1:]

        # Remove leading 00
        if phone.startswith('00'):
            phone = phone[2:]

        # Ensure we have a valid phone number
        if len(phone) < 7:
            return None

        return phone

    @staticmethod
    def normalize_email(email: Optional[str]) -> Optional[str]:
        """
        Normalize email address

        Args:
            email: Email address string

        Returns:
            Normalized email or None
        """
        if not email:
            return None

        # Strip whitespace
        email = email.strip()

        # Check for spaces in email (invalid)
        if ' ' in email:
            return None

        # Convert to lowercase
        email = email.lower()

        # Basic email validation
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return None

        return email

    @staticmethod
    def normalize_business_name(name: Optional[str]) -> Optional[str]:
        """
        Normalize business name for comparison

        Args:
            name: Business name string

        Returns:
            Normalized business name or None
        """
        if not name:
            return None

        # Strip whitespace
        name = name.strip()

        # Convert to title case
        name = name.title()

        # Remove common legal entity suffixes for comparison
        # Only remove if they appear at the end
        suffixes = [
            r'\s+LLC\.?$', r'\s+L\.L\.C\.?$', r'\s+Inc\.?$', r'\s+Ltd\.?$',
            r'\s+Limited$', r'\s+Corp\.?$', r'\s+Corporation$',
            r'\s+Co\.?$'
        ]

        for suffix in suffixes:
            name = re.sub(suffix, '', name, flags=re.IGNORECASE)

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()

        return name

    @staticmethod
    def normalize_website(website: Optional[str]) -> Optional[str]:
        """
        Normalize website URL

        Args:
            website: Website URL string

        Returns:
            Normalized website URL or None
        """
        if not website:
            return None

        # Strip whitespace
        website = website.strip()

        # Add protocol if missing
        if not website.startswith(('http://', 'https://')):
            website = 'https://' + website

        try:
            parsed = urlparse(website)
            # Ensure we have a valid domain
            if not parsed.netloc:
                return None

            # Normalize to lowercase
            normalized = f"{parsed.scheme}://{parsed.netloc.lower()}"
            if parsed.path:
                normalized += parsed.path

            return normalized
        except Exception:
            return None

    @staticmethod
    def normalize_address(address: Optional[str]) -> Optional[str]:
        """
        Normalize address

        Args:
            address: Address string

        Returns:
            Normalized address or None
        """
        if not address:
            return None

        # Strip whitespace
        address = address.strip()

        # Remove extra whitespace
        address = re.sub(r'\s+', ' ', address)

        # Convert to title case
        address = address.title()

        return address

    @staticmethod
    def normalize_city(city: Optional[str]) -> Optional[str]:
        """
        Normalize city name

        Args:
            city: City name string

        Returns:
            Normalized city name or None
        """
        if not city:
            return None

        # Strip whitespace
        city = city.strip()

        # Convert to title case
        city = city.title()

        return city

    @staticmethod
    def extract_domain(website: Optional[str]) -> Optional[str]:
        """
        Extract domain from website URL

        Args:
            website: Website URL string

        Returns:
            Domain name or None
        """
        if not website:
            return None

        try:
            normalized = DataNormalizer.normalize_website(website)
            if not normalized:
                return None

            parsed = urlparse(normalized)
            return parsed.netloc.lower()
        except Exception:
            return None

    @staticmethod
    def are_similar_names(name1: str, name2: str, threshold: float = 0.8) -> bool:
        """
        Check if two business names are similar using simple heuristic

        Args:
            name1: First business name
            name2: Second business name
            threshold: Similarity threshold (0-1)

        Returns:
            bool: True if names are similar
        """
        if not name1 or not name2:
            return False

        # Normalize both names
        norm1 = DataNormalizer.normalize_business_name(name1)
        norm2 = DataNormalizer.normalize_business_name(name2)

        if not norm1 or not norm2:
            return False

        # Check exact match
        if norm1 == norm2:
            return True

        # Check if one contains the other
        if norm1 in norm2 or norm2 in norm1:
            return True

        # Simple word overlap check
        words1 = set(norm1.split())
        words2 = set(norm2.split())

        if not words1 or not words2:
            return False

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        similarity = len(intersection) / len(union)

        return similarity >= threshold
