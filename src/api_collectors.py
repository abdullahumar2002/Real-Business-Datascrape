"""
API-based data collectors for free business data sources
"""

import logging
import requests
import os
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class CrunchbaseCollector:
    """Collect business data from Crunchbase API (free tier)"""

    def __init__(self, api_key: str = None):
        """
        Initialize Crunchbase collector
        
        Args:
            api_key: Crunchbase API key (optional, can use environment variable)
        """
        self.api_key = api_key or os.getenv('CRUNCHBASE_API_KEY')
        self.base_url = "https://api.crunchbase.com/api/v4"
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({
                'X-cb-user-key': self.api_key,
                'Content-Type': 'application/json'
            })
        else:
            logger.warning("No Crunchbase API key provided - using public data only")

    def search_organizations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for organizations on Crunchbase
        
        Args:
            query: Search query
            limit: Number of results to return
            
        Returns:
            List of organization data
        """
        if not self.api_key:
            logger.warning("Crunchbase API key required for search")
            return []
            
        try:
            url = f"{self.base_url}/entities/organizations"
            params = {
                'query': query,
                'limit': limit
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_organizations(data)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Crunchbase API error: {e}")
            return []

    def _parse_organizations(self, data: Dict) -> List[Dict]:
        """Parse Crunchbase organization data"""
        organizations = []
        
        if 'items' in data:
            for item in data['items']:
                org_data = item.get('properties', {})
                
                business = {
                    'business_name': org_data.get('name'),
                    'category': org_data.get('category'),
                    'website': org_data.get('website'),
                    'city': org_data.get('city'),
                    'country': org_data.get('country'),
                    'description': org_data.get('short_description'),
                    'founded_year': org_data.get('founded_on'),
                    'employee_count': org_data.get('num_employees_enum'),
                    'source': 'Crunchbase',
                    'source_url': f"https://www.crunchbase.com/organization/{org_data.get('web_url', '')}",
                    'source_type': 'api',
                    'source_verified': True
                }
                
                if business['business_name']:
                    organizations.append(business)
        
        return organizations


class GooglePlacesCollector:
    """Collect business data from Google Places API (free tier)"""

    def __init__(self, api_key: str = None):
        """
        Initialize Google Places collector
        
        Args:
            api_key: Google Places API key (optional, can use environment variable)
        """
        self.api_key = api_key or os.getenv('GOOGLE_PLACES_API_KEY')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.session = requests.Session()
        
        if not self.api_key:
            logger.warning("No Google Places API key provided - limited functionality")

    def search_places(self, query: str, location: str = None, radius: int = 50000, 
                     limit: int = 20) -> List[Dict]:
        """
        Search for places using Google Places API
        
        Args:
            query: Search query (e.g., "restaurants in Dubai")
            location: Location coordinates (lat,lng) or city name
            radius: Search radius in meters
            limit: Number of results to return
            
        Returns:
            List of place data
        """
        if not self.api_key:
            logger.warning("Google Places API key required for search")
            return []
            
        try:
            # First, get place ID from text search
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': query,
                'key': self.api_key,
                'radius': radius
            }
            
            if location:
                params['location'] = location
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                logger.warning(f"Google Places API error: {data.get('status')}")
                return []
            
            return self._parse_places(data.get('results', [])[:limit])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Places API error: {e}")
            return []

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Detailed place data
        """
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/details/json"
            params = {
                'place_id': place_id,
                'key': self.api_key,
                'fields': 'name,formatted_address,formatted_phone_number,website,rating,review_count,types,geometry'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'OK':
                return None
            
            return self._parse_place_details(data.get('result', {}))
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Google Places details error: {e}")
            return None

    def _parse_places(self, results: List[Dict]) -> List[Dict]:
        """Parse Google Places search results"""
        places = []
        
        for result in results:
            place = {
                'business_name': result.get('name'),
                'address': result.get('formatted_address'),
                'phone': result.get('formatted_phone_number'),
                'website': result.get('website'),
                'rating': result.get('rating'),
                'review_count': result.get('user_ratings_total'),
                'place_id': result.get('place_id'),
                'types': result.get('types', []),
                'location': result.get('geometry', {}).get('location'),
                'source': 'Google Places',
                'source_url': f"https://maps.google.com/?cid={result.get('place_id', '')}",
                'source_type': 'api',
                'source_verified': True
            }
            
            if place['business_name']:
                places.append(place)
        
        return places

    def _parse_place_details(self, result: Dict) -> Dict:
        """Parse detailed place information"""
        return {
            'business_name': result.get('name'),
            'address': result.get('formatted_address'),
            'phone': result.get('formatted_phone_number'),
            'website': result.get('website'),
            'rating': result.get('rating'),
            'review_count': result.get('user_ratings_total'),
            'types': result.get('types', []),
            'location': result.get('geometry', {}).get('location'),
            'source': 'Google Places',
            'source_url': f"https://maps.google.com/?cid={result.get('place_id', '')}",
            'source_type': 'api',
            'source_verified': True
        }


class GovernmentRegistryCollector:
    """Collect business data from government business registries"""

    def __init__(self):
        """Initialize government registry collector"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_uae_businesses(self, query: str, emirate: str = None) -> List[Dict]:
        """
        Search UAE business registries (DED registries)
        
        Args:
            query: Business name or search term
            emirate: Specific emirate (Dubai, Abu Dhabi, etc.)
            
        Returns:
            List of business data
        """
        # UAE has different DED registries for each emirate
        # This is a placeholder implementation
        # In reality, you'd need to check each emirate's specific registry
        
        businesses = []
        
        # Example for Dubai DED (placeholder)
        if emirate in ['Dubai', None]:
            dubai_businesses = self._search_dubai_ded(query)
            businesses.extend(dubai_businesses)
        
        # Example for Abu Dhabi DED (placeholder)
        if emirate in ['Abu Dhabi', None]:
            abu_dhabi_businesses = self._search_abu_dhabi_ded(query)
            businesses.extend(abu_dhabi_businesses)
        
        return businesses

    def search_usa_businesses(self, query: str, state: str = None) -> List[Dict]:
        """
        Search USA business registries (Secretary of State offices)
        
        Args:
            query: Business name or search term
            state: Specific state (CA, NY, TX, etc.)
            
        Returns:
            List of business data
        """
        # USA has different registries for each state
        # This is a placeholder implementation
        # In reality, you'd need to check each state's specific registry
        
        businesses = []
        
        # Example for California (placeholder)
        if state in ['CA', None]:
            ca_businesses = self._search_california_registry(query)
            businesses.extend(ca_businesses)
        
        # Example for New York (placeholder)
        if state in ['NY', None]:
            ny_businesses = self._search_new_york_registry(query)
            businesses.extend(ny_businesses)
        
        return businesses

    def _search_dubai_ded(self, query: str) -> List[Dict]:
        """Search Dubai Department of Economic Development registry"""
        # Placeholder - actual implementation would need to:
        # 1. Check Dubai DED's terms of service
        # 2. Use their official API if available
        # 3. Respect rate limits
        logger.info(f"Searching Dubai DED for: {query}")
        return []

    def _search_abu_dhabi_ded(self, query: str) -> List[Dict]:
        """Search Abu Dhabi Department of Economic Development registry"""
        # Placeholder - actual implementation would need to:
        # 1. Check Abu Dhabi DED's terms of service
        # 2. Use their official API if available
        # 3. Respect rate limits
        logger.info(f"Searching Abu Dhabi DED for: {query}")
        return []

    def _search_california_registry(self, query: str) -> List[Dict]:
        """Search California Secretary of State business registry"""
        # Placeholder - actual implementation would need to:
        # 1. Check California Secretary of State terms of service
        # 2. Use their official API if available
        # 3. Respect rate limits
        logger.info(f"Searching California registry for: {query}")
        return []

    def _search_new_york_registry(self, query: str) -> List[Dict]:
        """Search New York Department of State business registry"""
        # Placeholder - actual implementation would need to:
        # 1. Check New York Department of State terms of service
        # 2. Use their official API if available
        # 3. Respect rate limits
        logger.info(f"Searching New York registry for: {query}")
        return []