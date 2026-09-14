"""
Website verification and contact information extraction
"""

import logging
import re
from typing import Dict, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from src.crawler import Crawler
from src.normalizer import DataNormalizer

logger = logging.getLogger(__name__)


class WebsiteChecker:
    """Verifies websites and extracts official contact information"""

    def __init__(self, crawler: Crawler):
        """
        Initialize website checker

        Args:
            crawler: Crawler instance for making requests
        """
        self.crawler = crawler

    def check_website(self, website: str, business_name: str = None) -> Dict:
        """
        Check a website and extract information

        Args:
            website: Website URL
            business_name: Expected business name for verification

        Returns:
            Dictionary of website verification data
        """
        result = {
            'website_status': 'unreachable',
            'website_verified': False,
            'website_business_match': False,
            'https_enabled': False,
            'mobile_viewport': False,
            'contact_page_found': False,
            'social_links_found': False,
            'website_title': None,
            'website_quality_score': None,
            'official_email': None,
            'official_phone': None,
            'official_address': None,
        }

        if not website:
            return result

        try:
            # Normalize website
            normalized_website = DataNormalizer.normalize_website(website)
            if not normalized_website:
                logger.warning(f"Invalid website URL: {website}")
                return result

            # Check HTTPS
            parsed = urlparse(normalized_website)
            result['https_enabled'] = parsed.scheme == 'https'

            # Fetch the page
            response = self.crawler.get(normalized_website)
            if not response:
                result['website_status'] = 'unreachable'
                return result

            result['website_status'] = 'working'
            result['website_verified'] = True

            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract page title
            if soup.title:
                result['website_title'] = soup.title.get_text(strip=True)

            # Check for mobile viewport
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            result['mobile_viewport'] = viewport is not None

            # Check for contact page
            result['contact_page_found'] = self._check_contact_page(soup, normalized_website)

            # Check for social links
            result['social_links_found'] = self._check_social_links(soup)

            # Extract contact information
            result['official_email'] = self._extract_email(soup)
            result['official_phone'] = self._extract_phone(soup)
            result['official_address'] = self._extract_address(soup)

            # Verify business name match
            if business_name:
                result['website_business_match'] = self._verify_business_name(
                    soup, business_name
                )

            # Calculate quality score
            result['website_quality_score'] = self._calculate_quality_score(result)

            logger.info(f"Website check completed for {normalized_website}")

        except Exception as e:
            logger.error(f"Error checking website {website}: {e}")
            result['website_status'] = 'error'

        return result

    def _check_contact_page(self, soup: BeautifulSoup, base_url: str) -> bool:
        """Check if contact page exists"""
        # Look for contact links
        contact_selectors = [
            'a[href*="contact"]',
            'a[href*="Contact"]',
            'a[href*="CONTACT"]',
        ]

        for selector in contact_selectors:
            if soup.select_one(selector):
                return True

        return False

    def _check_social_links(self, soup: BeautifulSoup) -> bool:
        """Check for social media links"""
        social_domains = [
            'facebook.com', 'twitter.com', 'linkedin.com',
            'instagram.com', 'youtube.com'
        ]

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].lower()
            for domain in social_domains:
                if domain in href:
                    return True

        return False

    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract email from website"""
        # Look for mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE))
        for link in mailto_links:
            email = link['href'].replace('mailto:', '').split('?')[0]
            normalized = DataNormalizer.normalize_email(email)
            if normalized:
                return normalized

        # Look for email patterns in text
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        text = soup.get_text()
        matches = re.findall(email_pattern, text)
        if matches:
            normalized = DataNormalizer.normalize_email(matches[0])
            if normalized:
                return normalized

        return None

    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract phone number from website"""
        # Look for tel: links
        tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.IGNORECASE))
        for link in tel_links:
            phone = link['href'].replace('tel:', '')
            normalized = DataNormalizer.normalize_phone(phone)
            if normalized:
                return normalized

        # Look for phone patterns in text
        phone_patterns = [
            r'\+?[\d\s\-\(\)]{10,}',  # Various phone formats
        ]

        text = soup.get_text()
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                normalized = DataNormalizer.normalize_phone(matches[0])
                if normalized:
                    return normalized

        return None

    def _extract_address(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract address from website"""
        # Look for address in common locations
        address_selectors = [
            '[itemprop="address"]',
            '.address',
            '.location',
            '#address',
            '.contact-address',
        ]

        for selector in address_selectors:
            element = soup.select_one(selector)
            if element:
                address = element.get_text(strip=True)
                if address and len(address) > 10:
                    return address

        return None

    def _verify_business_name(self, soup: BeautifulSoup, expected_name: str) -> bool:
        """
        Verify if website matches expected business name

        Args:
            soup: BeautifulSoup object
            expected_name: Expected business name

        Returns:
            bool: True if likely match
        """
        if not expected_name:
            return False

        # Check page title
        if soup.title:
            title = soup.title.get_text(strip=True).lower()
            if expected_name.lower() in title:
                return True

        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].lower()
            if expected_name.lower() in desc:
                return True

        # Check h1 tag
        h1 = soup.find('h1')
        if h1:
            h1_text = h1.get_text(strip=True).lower()
            if expected_name.lower() in h1_text:
                return True

        # Use normalized comparison
        page_text = soup.get_text().lower()
        normalized_expected = DataNormalizer.normalize_business_name(expected_name)
        if normalized_expected:
            if normalized_expected.lower() in page_text:
                return True

        return False

    def _calculate_quality_score(self, result: Dict) -> int:
        """
        Calculate website quality score (0-100)

        Args:
            result: Website check result dictionary

        Returns:
            int: Quality score
        """
        score = 0

        if result['https_enabled']:
            score += 20

        if result['mobile_viewport']:
            score += 15

        if result['contact_page_found']:
            score += 15

        if result['social_links_found']:
            score += 10

        if result['official_email']:
            score += 15

        if result['official_phone']:
            score += 15

        if result['official_address']:
            score += 10

        return score
