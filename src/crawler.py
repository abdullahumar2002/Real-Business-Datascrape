"""
Web crawler with rate limiting, safety checks, and error handling
"""

import time
import random
import logging
import requests
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Crawler:
    """Web crawler with rate limiting and safety features"""

    def __init__(self, delay_min: float = 2.0, delay_max: float = 5.0,
                 timeout: int = 30, max_retries: int = 3):
        """
        Initialize crawler

        Args:
            delay_min: Minimum delay between requests (seconds)
            delay_max: Maximum delay between requests (seconds)
            timeout: Request timeout (seconds)
            max_retries: Maximum number of retries for failed requests
        """
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _delay(self):
        """Apply random delay between requests"""
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)

    def _should_retry(self, status_code: int, error: Exception = None) -> bool:
        """
        Determine if a request should be retried

        Args:
            status_code: HTTP status code
            error: Exception if any

        Returns:
            bool: True if should retry
        """
        # Don't retry on client errors that indicate permanent issues
        if status_code in (401, 403, 404):
            return False

        # Don't retry on rate limiting (429) - will wait and retry differently
        if status_code == 429:
            return True

        # Retry on server errors and network issues
        if status_code >= 500 or error is not None:
            return True

        return False

    def _get_retry_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay

        Args:
            attempt: Current attempt number

        Returns:
            float: Delay in seconds
        """
        return min(2 ** attempt, 10)  # Cap at 10 seconds

    def get(self, url: str, params: dict = None, headers: dict = None) -> Optional[requests.Response]:
        """
        Perform HTTP GET request with retries and rate limiting

        Args:
            url: URL to fetch
            params: Query parameters
            headers: Additional headers

        Returns:
            Response object or None if failed
        """
        self._delay()

        for attempt in range(self.max_retries):
            try:
                if headers:
                    merged_headers = {**self.session.headers, **headers}
                else:
                    merged_headers = self.session.headers

                response = self.session.get(
                    url,
                    params=params,
                    headers=merged_headers,
                    timeout=self.timeout,
                    allow_redirects=True
                )

                # Check if we should retry
                if response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = self._get_retry_delay(attempt + 1)
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                    continue

                if response.status_code >= 400:
                    if self._should_retry(response.status_code):
                        wait_time = self._get_retry_delay(attempt)
                        logger.warning(f"Request failed with status {response.status_code}, "
                                     f"retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.error(f"Request failed with status {response.status_code}, not retrying")
                        return None

                return response

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    wait_time = self._get_retry_delay(attempt)
                    logger.warning(f"Request timeout, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request timeout after {self.max_retries} attempts")
                    return None

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = self._get_retry_delay(attempt)
                    logger.warning(f"Request error: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Request failed after {self.max_retries} attempts: {e}")
                    return None

        return None

    def head(self, url: str) -> Optional[requests.Response]:
        """
        Perform HTTP HEAD request

        Args:
            url: URL to check

        Returns:
            Response object or None if failed
        """
        self._delay()

        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            return response
        except Exception as e:
            logger.error(f"HEAD request failed for {url}: {e}")
            return None

    def parse_html(self, response: requests.Response) -> BeautifulSoup:
        """
        Parse HTML response

        Args:
            response: Response object

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(response.text, 'lxml')

    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """
        Extract all links from HTML

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        return links

    def extract_text(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """
        Extract text from HTML using CSS selector

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            Extracted text or None
        """
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
        return None

    def extract_multiple_texts(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """
        Extract multiple texts from HTML using CSS selector

        Args:
            soup: BeautifulSoup object
            selector: CSS selector

        Returns:
            List of extracted texts
        """
        elements = soup.select(selector)
        return [e.get_text(strip=True) for e in elements]

    def extract_attribute(self, soup: BeautifulSoup, selector: str, attribute: str) -> Optional[str]:
        """
        Extract attribute from HTML element

        Args:
            soup: BeautifulSoup object
            selector: CSS selector
            attribute: Attribute name

        Returns:
            Attribute value or None
        """
        element = soup.select_one(selector)
        if element:
            return element.get(attribute)
        return None

    def close(self):
        """Close the session"""
        self.session.close()
