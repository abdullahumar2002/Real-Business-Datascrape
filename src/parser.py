"""
Generic parser for extracting business data from various sources
"""

import logging
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class BusinessParser:
    """Generic business data parser"""

    def __init__(self, source_config: dict):
        """
        Initialize parser

        Args:
            source_config: Source configuration dictionary
        """
        self.source_config = source_config
        self.source_name = source_config.get('name', 'Unknown')
        self.source_type = source_config.get('source_type', 'directory')
        self.parser_type = source_config.get('parser', 'generic')

    def parse_business_page(self, html: str, url: str) -> Optional[Dict]:
        """
        Parse a business listing page

        Args:
            html: HTML content
            url: Source URL

        Returns:
            Dictionary of extracted business data or None
        """
        try:
            soup = BeautifulSoup(html, 'lxml')

            business_data = {
                'source': self.source_name,
                'source_url': url,
                'source_type': self.source_type,
                'source_verified': True,
            }

            # Try to extract common fields
            # These are generic selectors - can be overridden per source
            business_data['business_name'] = self._extract_business_name(soup)
            business_data['category'] = self._extract_category(soup)
            business_data['address'] = self._extract_address(soup)
            business_data['phone'] = self._extract_phone(soup)
            business_data['email'] = self._extract_email(soup)
            business_data['website'] = self._extract_website(soup, url)
            business_data['rating'] = self._extract_rating(soup)
            business_data['review_count'] = self._extract_review_count(soup)
            business_data['city'] = self._extract_city(soup)
            business_data['country'] = self.source_config.get('country', 'Unknown')

            # Validate that we have at least a business name
            if not business_data['business_name']:
                logger.warning(f"No business name found on {url}")
                return None

            return business_data

        except Exception as e:
            logger.error(f"Error parsing business page {url}: {e}")
            return None

    def _extract_business_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract business name from page"""
        # Try common selectors
        selectors = [
            'h1',
            '.business-name',
            '.company-name',
            '[itemprop="name"]',
            '.title',
            'h2',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = element.get_text(strip=True)
                if name and len(name) > 2:  # Minimum length check
                    return name

        return None

    def _extract_category(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract business category"""
        selectors = [
            '[itemprop="category"]',
            '.category',
            '.business-category',
            '.industry',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address"""
        selectors = [
            '[itemprop="address"]',
            '.address',
            '.location',
            '.street-address',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return None

    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract phone number"""
        selectors = [
            '[itemprop="telephone"]',
            '.phone',
            '.telephone',
            'a[href^="tel:"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'a':
                    phone = element.get('href', '').replace('tel:', '')
                else:
                    phone = element.get_text(strip=True)
                if phone:
                    return phone

        return None

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email address"""
        selectors = [
            '[itemprop="email"]',
            '.email',
            'a[href^="mailto:"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'a':
                    email = element.get('href', '').replace('mailto:', '')
                else:
                    email = element.get_text(strip=True)
                if email and '@' in email:
                    return email

        return None

    def _extract_website(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract website URL"""
        selectors = [
            '[itemprop="url"]',
            '.website',
            'a[href^="http"]',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'a':
                    website = element.get('href')
                else:
                    website = element.get_text(strip=True)

                if website:
                    # Make absolute URL
                    website = urljoin(base_url, website)
                    return website

        return None

    def _extract_rating(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract rating"""
        selectors = [
            '[itemprop="ratingValue"]',
            '.rating',
            '.stars',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                try:
                    rating_text = element.get_text(strip=True)
                    # Try to extract number
                    import re
                    match = re.search(r'(\d+\.?\d*)', rating_text)
                    if match:
                        return float(match.group(1))
                except (ValueError, AttributeError):
                    continue

        return None

    def _extract_review_count(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract review count"""
        selectors = [
            '[itemprop="reviewCount"]',
            '.review-count',
            '.reviews',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                try:
                    review_text = element.get_text(strip=True)
                    # Try to extract number
                    import re
                    match = re.search(r'(\d+)', review_text)
                    if match:
                        return int(match.group(1))
                except (ValueError, AttributeError):
                    continue

        return None

    def _extract_city(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract city"""
        selectors = [
            '[itemprop="addressLocality"]',
            '.city',
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        return None
