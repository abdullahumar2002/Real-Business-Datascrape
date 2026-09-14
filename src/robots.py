"""
Robots.txt checker and automation permission handler
"""

import logging
import urllib.robotparser
from urllib.parse import urlparse
from typing import Tuple, Optional
import requests

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Checks robots.txt and automation permissions"""

    def __init__(self, user_agent: str = "BusinessLeadAgent/1.0"):
        """
        Initialize robots checker

        Args:
            user_agent: User agent string for robots.txt checks
        """
        self.user_agent = user_agent
        self.cache = {}  # Cache robots.txt results

    def check_robots_txt(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if URL is allowed by robots.txt

        Args:
            url: URL to check

        Returns:
            Tuple of (allowed, reason)
        """
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

            # Check cache
            if robots_url in self.cache:
                return self.cache[robots_url]

            # Fetch robots.txt
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 404:
                # No robots.txt means all paths are allowed
                result = (True, None)
                self.cache[robots_url] = result
                return result

            if response.status_code != 200:
                logger.warning(f"Failed to fetch robots.txt: {robots_url} (status: {response.status_code})")
                result = (True, "robots.txt unavailable")  # Allow if can't check
                self.cache[robots_url] = result
                return result

            # Parse robots.txt
            rp = urllib.robotparser.RobotFileParser()
            rp.parse(response.text.splitlines())

            allowed = rp.can_fetch(self.user_agent, url)
            reason = None if allowed else "Disallowed by robots.txt"

            result = (allowed, reason)
            self.cache[robots_url] = result
            return result

        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            # Allow if check fails (better to proceed cautiously than block)
            return (True, f"robots.txt check failed: {str(e)}")

    def is_automation_allowed(self, source_config: dict) -> Tuple[bool, str]:
        """
        Check if automation is allowed based on source configuration

        Args:
            source_config: Source configuration dictionary

        Returns:
            Tuple of (allowed, status_code)
        """
        # Check explicit configuration
        if not source_config.get('allowed', False):
            return (False, 'AUTOMATION_NOT_ALLOWED')

        # Check automation_allowed flag
        if not source_config.get('automation_allowed', True):
            return (False, 'AUTOMATION_NOT_ALLOWED')

        # Check if manual export is required
        if source_config.get('requires_manual_export', False):
            return (False, 'REQUIRES_MANUAL_EXPORT')

        # Check if API is required
        if source_config.get('requires_api_key', False):
            return (False, 'REQUIRES_API')

        # Check robots.txt for directory sources
        if source_config.get('source_type') == 'directory':
            url = source_config.get('url')
            if url:
                allowed, reason = self.check_robots_txt(url)
                if not allowed:
                    return (False, f'BLOCKED: {reason}')

        return (True, 'ALLOWED')

    def get_source_status(self, source_config: dict) -> str:
        """
        Get the overall status of a source

        Args:
            source_config: Source configuration dictionary

        Returns:
            str: Status code (ALLOWED, BLOCKED, AUTOMATION_NOT_ALLOWED, etc.)
        """
        allowed, status = self.is_automation_allowed(source_config)
        return status
