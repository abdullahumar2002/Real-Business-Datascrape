"""
Source manager for loading and managing business data sources
"""

import yaml
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SourceManager:
    """Manages business data sources from configuration"""

    def __init__(self, config_path: str = "config/sources.yaml"):
        """
        Initialize source manager

        Args:
            config_path: Path to sources configuration file
        """
        self.config_path = config_path
        self.sources = []
        self._load_sources()

    def _load_sources(self):
        """Load sources from configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.sources = config.get('sources', [])
            logger.info(f"Loaded {len(self.sources)} sources from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Sources config not found at {self.config_path}, using empty list")
            self.sources = []
        except Exception as e:
            logger.error(f"Error loading sources: {e}")
            self.sources = []

    def get_sources(self) -> List[Dict]:
        """
        Get all sources

        Returns:
            List of source dictionaries
        """
        return self.sources

    def get_sources_by_country(self, country: str) -> List[Dict]:
        """
        Get sources for a specific country

        Args:
            country: Country name (UAE, USA)

        Returns:
            List of source dictionaries
        """
        return [s for s in self.sources if s.get('country') == country]

    def get_allowed_sources(self) -> List[Dict]:
        """
        Get sources that are allowed for automation

        Returns:
            List of source dictionaries
        """
        return [s for s in self.sources if s.get('allowed', False)]

    def get_allowed_sources_by_country(self, country: str) -> List[Dict]:
        """
        Get allowed sources for a specific country

        Args:
            country: Country name

        Returns:
            List of source dictionaries
        """
        return [s for s in self.sources
                if s.get('country') == country and s.get('allowed', False)]

    def get_source_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a source by name

        Args:
            name: Source name

        Returns:
            Source dictionary or None
        """
        for source in self.sources:
            if source.get('name') == name:
                return source
        return None

    def get_sources_by_type(self, source_type: str) -> List[Dict]:
        """
        Get sources by type

        Args:
            source_type: Source type (directory, api, etc.)

        Returns:
            List of source dictionaries
        """
        return [s for s in self.sources if s.get('source_type') == source_type]

    def get_prioritized_sources(self, country: str = None) -> List[Dict]:
        """
        Get sources sorted by priority

        Args:
            country: Optional country filter

        Returns:
            List of source dictionaries sorted by priority
        """
        sources = self.get_allowed_sources()
        if country:
            sources = [s for s in sources if s.get('country') == country]

        return sorted(sources, key=lambda x: x.get('priority', 999))

    def has_allowed_sources(self, country: str = None) -> bool:
        """
        Check if there are any allowed sources

        Args:
            country: Optional country filter

        Returns:
            bool: True if allowed sources exist
        """
        sources = self.get_allowed_sources()
        if country:
            sources = [s for s in sources if s.get('country') == country]
        return len(sources) > 0

    def count_allowed_sources(self, country: str = None) -> int:
        """
        Count allowed sources

        Args:
            country: Optional country filter

        Returns:
            int: Number of allowed sources
        """
        sources = self.get_allowed_sources()
        if country:
            sources = [s for s in sources if s.get('country') == country]
        return len(sources)
