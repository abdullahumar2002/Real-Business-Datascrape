"""
Multi-source data collection system for business data
"""

import logging
from typing import Dict, List, Optional
from src.api_collectors import CrunchbaseCollector, GooglePlacesCollector, GovernmentRegistryCollector
from src.crawler import Crawler
from src.parser import BusinessParser
from src.database import DatabaseManager
from src.free_scrapers import PublicDirectoryScraper, GovernmentBusinessRegistry, OpenBusinessDataCollector, EnhancedSampleGenerator

logger = logging.getLogger(__name__)


class MultiSourceDataCollector:
    """Collect business data from multiple sources"""

    def __init__(self, db_manager: DatabaseManager, crawler: Crawler):
        """
        Initialize multi-source data collector
        
        Args:
            db_manager: Database manager instance
            crawler: Web crawler instance
        """
        self.db_manager = db_manager
        self.crawler = crawler
        
        # Initialize API collectors
        self.crunchbase_collector = CrunchbaseCollector()
        self.google_places_collector = GooglePlacesCollector()
        self.gov_collector = GovernmentRegistryCollector()
        self.sample_generator = EnhancedSampleGenerator()
        
        # Initialize free data collectors
        self.public_directory_scraper = PublicDirectoryScraper()
        self.gov_business_registry = GovernmentBusinessRegistry()
        self.open_data_collector = OpenBusinessDataCollector()
        
        # Collection statistics
        self.stats = {
            'total_collected': 0,
            'crunchbase': 0,
            'google_places': 0,
            'government': 0,
            'web_scraping': 0,
            'sample_data': 0,
            'open_data': 0,
            'errors': 0
        }

    def collect_businesses(self, target: int = 500, countries: List[str] = ['UAE', 'USA']) -> Dict:
        """
        Collect businesses from multiple sources
        
        Args:
            target: Target number of businesses to collect per country
            countries: List of countries to collect from
            
        Returns:
            Collection statistics
        """
        logger.info(f"Starting multi-source data collection: target={target} per country, countries={countries}")
        
        for country in countries:
            self._collect_for_country(country, target)
        
        logger.info(f"Data collection complete: {self.stats}")
        return self.stats

    def _collect_for_country(self, country: str, target: int):
        """
        Collect businesses for a specific country
        
        Args:
            country: Country name
            target: Target number of businesses
        """
        logger.info(f"Collecting {target} businesses for {country}")
        
        country_collected = 0
        
        # Try different sources (prioritizing fast free sources)
        sources_tried = 0
        max_sources = 4  # Try up to 4 different sources including sample data
        
        while country_collected < target and sources_tried < max_sources:
            if sources_tried == 0:
                # Try free open data sources first (GitHub - fast)
                collected = self._collect_from_open_data(country, target - country_collected)
                country_collected += collected
            elif sources_tried == 1:
                # Try government registries (fast if implemented)
                collected = self._collect_from_government_registries(country, target - country_collected)
                country_collected += collected
            elif sources_tried == 2:
                # Try Google Places (if API key available)
                collected = self._collect_from_google_places(country, target - country_collected)
                country_collected += collected
            elif sources_tried == 3:
                # Generate enhanced sample data as fallback (fast and realistic)
                collected = self._collect_from_sample_data(country, target - country_collected)
                country_collected += collected
            
            sources_tried += 1
        
        logger.info(f"Collected {country_collected} businesses for {country}")

    def _collect_from_google_places(self, country: str, target: int) -> int:
        """
        Collect businesses from Google Places API
        
        Args:
            country: Country name
            target: Target number of businesses
            
        Returns:
            Number of businesses collected
        """
        logger.info(f"Collecting from Google Places for {country}")
        
        collected_count = 0
        
        # Define search queries based on country
        if country == 'UAE':
            queries = [
                "restaurants in Dubai",
                "hotels in Abu Dhabi", 
                "technology companies in Dubai",
                "construction companies in UAE",
                "medical clinics in Dubai"
            ]
            locations = ["25.2048,55.2708"]  # Dubai coordinates
        else:  # USA
            queries = [
                "restaurants in New York",
                "hotels in Los Angeles",
                "technology companies in San Francisco",
                "construction companies in Chicago",
                "medical clinics in Houston"
            ]
            locations = ["40.7128,-74.0060"]  # NYC coordinates
        
        for query in queries:
            if collected_count >= target:
                break
                
            try:
                places = self.google_places_collector.search_places(
                    query=query,
                    location=locations[0],
                    limit=20
                )
                
                for place in places:
                    if self._add_business_to_database(place, country):
                        self.stats['google_places'] += 1
                        self.stats['total_collected'] += 1
                        collected_count += 1
                        
                        if collected_count >= target:
                            break
                            
            except Exception as e:
                logger.error(f"Error collecting from Google Places: {e}")
                self.stats['errors'] += 1
        
        return collected_count

    def _collect_from_crunchbase(self, country: str, target: int) -> int:
        """
        Collect businesses from Crunchbase API
        
        Args:
            country: Country name
            target: Target number of businesses
            
        Returns:
            Number of businesses collected
        """
        logger.info(f"Collecting from Crunchbase for {country}")
        
        collected_count = 0
        
        # Define search queries based on country
        if country == 'UAE':
            queries = ["technology", "construction", "healthcare", "finance"]
        else:  # USA
            queries = ["technology", "construction", "healthcare", "finance"]
        
        for query in queries:
            if collected_count >= target:
                break
                
            try:
                organizations = self.crunchbase_collector.search_organizations(
                    query=query,
                    limit=10
                )
                
                for org in organizations:
                    if self._add_business_to_database(org, country):
                        self.stats['crunchbase'] += 1
                        self.stats['total_collected'] += 1
                        collected_count += 1
                        
                        if collected_count >= target:
                            break
                            
            except Exception as e:
                logger.error(f"Error collecting from Crunchbase: {e}")
                self.stats['errors'] += 1
        
        return collected_count

    def _collect_from_open_data(self, country: str, target: int) -> int:
        """
        Collect businesses from free open data sources
        
        Args:
            country: Country name
            target: Target number of businesses
            
        Returns:
            Number of businesses collected
        """
        logger.info(f"Collecting from open data sources for {country}")
        
        collected_count = 0
        
        try:
            # Try OpenCorporates (free API)
            jurisdiction = "ae" if country == "UAE" else "us"
            queries = ["technology", "construction", "healthcare", "financial"]
            
            for query in queries:
                if collected_count >= target:
                    break
                    
                businesses = self.open_data_collector.collect_from_opencorporates(
                    query=query,
                    jurisdiction=jurisdiction,
                    limit=min(10, target - collected_count)
                )
                
                for business in businesses:
                    if self._add_business_to_database(business, country):
                        self.stats['open_data'] += 1
                        self.stats['total_collected'] += 1
                        collected_count += 1
                        
                        if collected_count >= target:
                            break
            
            # Try GitHub for technology companies
            if collected_count < target:
                tech_companies = self.open_data_collector.collect_from_github_companies(
                    category="technology",
                    limit=min(20, target - collected_count)
                )
                
                for business in tech_companies:
                    if self._add_business_to_database(business, country):
                        self.stats['open_data'] += 1
                        self.stats['total_collected'] += 1
                        collected_count += 1
                        
                        if collected_count >= target:
                            break
                            
        except Exception as e:
            logger.error(f"Error collecting from open data: {e}")
            self.stats['errors'] += 1
        
        return collected_count

    def _collect_from_government_registries(self, country: str, target: int) -> int:
        """
        Collect businesses from government registries
        
        Args:
            country: Country name
            target: Target number of businesses
            
        Returns:
            Number of businesses collected
        """
        logger.info(f"Collecting from government registries for {country}")
        
        collected_count = 0
        
        # Define search queries
        queries = ["construction", "technology", "healthcare", "retail"]
        
        for query in queries:
            if collected_count >= target:
                break
                
            try:
                if country == 'UAE':
                    businesses = self.gov_collector.search_uae_businesses(query)
                else:  # USA
                    businesses = self.gov_collector.search_usa_businesses(query)
                
                for business in businesses:
                    if self._add_business_to_database(business, country):
                        self.stats['government'] += 1
                        self.stats['total_collected'] += 1
                        collected_count += 1
                        
                        if collected_count >= target:
                            break
                            
            except Exception as e:
                logger.error(f"Error collecting from government registries: {e}")
                self.stats['errors'] += 1
        
        return collected_count

    def _collect_from_web_scraping(self, country: str, target: int) -> int:
        """
        Collect businesses from web scraping
        
        Args:
            country: Country name
            target: Target number of businesses
            
        Returns:
            Number of businesses collected
        """
        logger.info(f"Collecting from web scraping for {country}")
        
        collected_count = 0
        
        # Define business directories to scrape
        # This is a placeholder - actual implementation would need:
        # 1. Check robots.txt for each site
        # 2. Respect terms of service
        # 3. Use appropriate rate limits
        
        if country == 'UAE':
            directories = [
                "https://example-uae-directory.com/business"
            ]
        else:  # USA
            directories = [
                "https://example-usa-directory.com/business"
            ]
        
        for directory_url in directories:
            if collected_count >= target:
                break
                
            try:
                response = self.crawler.get(directory_url)
                if response:
                    soup = self.crawler.parse_html(response)
                    parser = BusinessParser({
                        'name': 'Web Directory',
                        'country': country,
                        'source_type': 'directory'
                    })
                    
                    # Extract business links
                    links = self.crawler.extract_links(soup, directory_url)
                    
                    for link in links[:10]:  # Limit to 10 for testing
                        if collected_count >= target:
                            break
                            
                        try:
                            business_response = self.crawler.get(link)
                            if business_response:
                                business_data = parser.parse_business_page(
                                    business_response.text, 
                                    link
                                )
                                
                                if business_data and self._add_business_to_database(business_data, country):
                                    self.stats['web_scraping'] += 1
                                    self.stats['total_collected'] += 1
                                    collected_count += 1
                                    
                        except Exception as e:
                            logger.error(f"Error scraping business page: {e}")
                            self.stats['errors'] += 1
                            
            except Exception as e:
                logger.error(f"Error scraping directory: {e}")
                self.stats['errors'] += 1
        
        return collected_count

    def _collect_from_sample_data(self, country: str, target: int) -> int:
        """
        Generate enhanced sample business data as fallback
        
        Args:
            country: Country name
            target: Target number of businesses
            
        Returns:
            Number of businesses collected
        """
        logger.info(f"Generating enhanced sample data for {country}")
        
        collected_count = 0
        
        try:
            sample_businesses = self.sample_generator.generate_realistic_businesses(country, target)
            
            for business in sample_businesses:
                if self._add_business_to_database(business, country):
                    self.stats['sample_data'] += 1
                    self.stats['total_collected'] += 1
                    collected_count += 1
                    
                    if collected_count >= target:
                        break
                        
        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            self.stats['errors'] += 1
        
        return collected_count

    def _add_business_to_database(self, business_data: Dict, country: str) -> bool:
        """
        Add business data to database
        
        Args:
            business_data: Business data dictionary
            country: Country name
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Normalize business data for database
            normalized_data = self._normalize_business_data(business_data, country)
            
            # Check for duplicates
            if normalized_data.get('website'):
                existing = self.db_manager.get_business_by_website(normalized_data['website'])
                if existing:
                    logger.debug(f"Duplicate business (website): {normalized_data['business_name']}")
                    return False
            
            # Add to database
            self.db_manager.add_business(normalized_data)
            logger.debug(f"Added business: {normalized_data['business_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding business to database: {e}")
            return False

    def _normalize_business_data(self, business_data: Dict, country: str) -> Dict:
        """
        Normalize business data for database insertion
        
        Args:
            business_data: Raw business data
            country: Country name
            
        Returns:
            Normalized business data
        """
        # Extract data with fallbacks
        normalized = {
            'business_name': business_data.get('business_name') or business_data.get('name'),
            'category': business_data.get('category') or business_data.get('types', [''])[0] if business_data.get('types') else None,
            'address': business_data.get('address'),
            'city': business_data.get('city') or self._extract_city_from_address(business_data.get('address')),
            'state': business_data.get('state'),
            'country': country,
            'phone': business_data.get('phone') or business_data.get('formatted_phone_number'),
            'email': business_data.get('email'),
            'website': business_data.get('website'),
            'rating': business_data.get('rating'),
            'review_count': business_data.get('review_count') or business_data.get('user_ratings_total'),
            'source': business_data.get('source', 'Unknown'),
            'source_url': business_data.get('source_url'),
            'source_type': business_data.get('source_type', 'api'),
            'source_verified': business_data.get('source_verified', True),
            'verification_status': 'PENDING'
        }
        
        # Remove None values
        return {k: v for k, v in normalized.items() if v is not None}

    def _extract_city_from_address(self, address: str) -> Optional[str]:
        """Extract city from address string"""
        if not address:
            return None
            
        # Simple extraction - in reality, would use geocoding
        cities = ['Dubai', 'Abu Dhabi', 'New York', 'Los Angeles', 'Chicago', 'Houston']
        for city in cities:
            if city.lower() in address.lower():
                return city
        
        return None