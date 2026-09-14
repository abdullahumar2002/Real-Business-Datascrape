"""
Free business data scrapers for public data sources (no API keys required)
"""

import logging
import requests
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re
import time
import random

logger = logging.getLogger(__name__)


class PublicDirectoryScraper:
    """Scraper for public business directories that allow data collection"""

    def __init__(self):
        """Initialize public directory scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def scrape_craigslist_businesses(self, city: str, category: str = "bzb", limit: int = 50) -> List[Dict]:
        """
        Scrape Craigslist business listings (publicly accessible)
        
        Args:
            city: City name (e.g., "dubai", "newyork")
            category: Craigslist category code
            limit: Number of listings to scrape
            
        Returns:
            List of business data
        """
        try:
            url = f"https://{city}.craigslist.org/search/{category}"
            logger.info(f"Scraping Craigslist for {city}")
            
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Craigslist returned status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'lxml')
            businesses = []
            
            # Parse Craigslist listings
            listings = soup.find_all('li', class_='result-row')
            
            for listing in listings[:limit]:
                try:
                    title_elem = listing.find('a', class_='result-title')
                    price_elem = listing.find('span', class_='result-price')
                    location_elem = listing.find('span', class_='result-hood')
                    link_elem = listing.find('a', class_='result-title')
                    
                    if title_elem:
                        business = {
                            'business_name': title_elem.get_text(strip=True),
                            'category': category,
                            'address': location_elem.get_text(strip=True) if location_elem else None,
                            'city': city,
                            'country': 'USA' if city.lower() in ['newyork', 'losangeles', 'chicago'] else 'UAE',
                            'phone': None,
                            'email': None,
                            'website': link_elem.get('href') if link_elem else None,
                            'rating': None,
                            'review_count': None,
                            'source': 'Craigslist',
                            'source_url': link_elem.get('href') if link_elem else url,
                            'source_type': 'directory',
                            'source_verified': True
                        }
                        
                        if business['business_name']:
                            businesses.append(business)
                
                except Exception as e:
                    logger.debug(f"Error parsing Craigslist listing: {e}")
                    continue
            
            logger.info(f"Scraped {len(businesses)} businesses from Craigslist")
            return businesses
            
        except Exception as e:
            logger.error(f"Error scraping Craigslist: {e}")
            return []

    def scrape_yellow_pages_alternative(self, city: str, category: str, limit: int = 30) -> List[Dict]:
        """
        Scrape alternative business directories (respecting terms of service)
        
        Args:
            city: City name
            category: Business category
            limit: Number of results to scrape
            
        Returns:
            List of business data
        """
        try:
            # Using a sample approach - in reality, you'd need to check each directory's terms
            # This is a template for how to implement free directory scraping
            
            logger.info(f"Searching business directories for {category} in {city}")
            
            # Placeholder for actual directory scraping
            # In reality, you would:
            # 1. Check robots.txt
            # 2. Review terms of service
            # 3. Implement rate limiting
            # 4. Parse specific HTML structure
            
            return []
            
        except Exception as e:
            logger.error(f"Error scraping business directory: {e}")
            return []


class GovernmentBusinessRegistry:
    """Scraper for government business registries (publicly accessible)"""

    def __init__(self):
        """Initialize government registry scraper"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_uae_free_zones(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search UAE free zone business registries (many are publicly accessible)
        
        Args:
            query: Business name or search term
            limit: Number of results
            
        Returns:
            List of business data
        """
        try:
            # UAE free zones often have public business search
            # Examples: JAFZA, DAFZA, DMCC, etc.
            
            logger.info(f"Searching UAE free zones for: {query}")
            
            # Placeholder for actual implementation
            # In reality, you would scrape specific free zone portals
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching UAE free zones: {e}")
            return []

    def search_usa_public_records(self, state: str, query: str, limit: int = 20) -> List[Dict]:
        """
        Search USA public business records (many states have free online search)
        
        Args:
            state: State abbreviation (CA, NY, TX, etc.)
            query: Business name or search term
            limit: Number of results
            
        Returns:
            List of business data
        """
        try:
            # Many US states have free business entity search
            # Examples: California, New York, Texas, Florida
            
            logger.info(f"Searching {state} public records for: {query}")
            
            # Placeholder for actual implementation
            # In reality, you would scrape specific state business portals
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching USA public records: {e}")
            return []


class OpenBusinessDataCollector:
    """Collector for open business data sources"""

    def __init__(self):
        """Initialize open data collector"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def collect_from_opencorporates(self, query: str, jurisdiction: str = "us", limit: int = 20) -> List[Dict]:
        """
        Collect from OpenCorporates (open database of companies)
        
        Args:
            query: Company name search
            jurisdiction: Country code (us, ae, etc.)
            limit: Number of results
            
        Returns:
            List of business data
        """
        try:
            # OpenCorporates has a free API for basic data
            url = f"https://api.opencorporates.com/companies/search"
            params = {
                'q': query,
                'jurisdiction_code': jurisdiction,
                'per_page': limit
            }
            
            logger.info(f"Searching OpenCorporates for: {query} in {jurisdiction}")
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"OpenCorporates returned status {response.status_code}")
                return []
            
            data = response.json()
            businesses = []
            
            if 'results' in data:
                for company in data['results']['companies']:
                    company_data = company['company']
                    
                    business = {
                        'business_name': company_data.get('name'),
                        'category': company_data.get('company_type'),
                        'address': company_data.get('registered_address_in_full'),
                        'city': None,
                        'country': jurisdiction.upper(),
                        'phone': None,
                        'email': None,
                        'website': None,
                        'rating': None,
                        'review_count': None,
                        'source': 'OpenCorporates',
                        'source_url': company_data.get('opencorporates_url'),
                        'source_type': 'api',
                        'source_verified': True
                    }
                    
                    if business['business_name']:
                        businesses.append(business)
            
            logger.info(f"Collected {len(businesses)} businesses from OpenCorporates")
            return businesses
            
        except Exception as e:
            logger.error(f"Error collecting from OpenCorporates: {e}")
            return []

    def collect_from_github_companies(self, category: str = "technology", limit: int = 20) -> List[Dict]:
        """
        Collect technology companies from GitHub (open source projects)
        
        Args:
            category: Technology category
            limit: Number of results
            
        Returns:
            List of business data
        """
        try:
            # GitHub has many companies with open source projects
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f'organization:{category}',
                'sort': 'stars',
                'order': 'desc',
                'per_page': limit
            }
            
            logger.info(f"Searching GitHub for {category} companies")
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code != 200:
                logger.warning(f"GitHub returned status {response.status_code}")
                return []
            
            data = response.json()
            businesses = []
            
            if 'items' in data:
                for repo in data['items']:
                    org_name = repo.get('owner', {}).get('login')
                    
                    business = {
                        'business_name': org_name,
                        'category': 'Technology',
                        'address': None,
                        'city': None,
                        'country': 'USA',  # Most GitHub companies are US-based
                        'phone': None,
                        'email': None,
                        'website': repo.get('owner', {}).get('html_url'),
                        'rating': repo.get('stargazers_count'),
                        'review_count': repo.get('watchers_count'),
                        'source': 'GitHub',
                        'source_url': repo.get('html_url'),
                        'source_type': 'api',
                        'source_verified': True
                    }
                    
                    if business['business_name']:
                        businesses.append(business)
            
            logger.info(f"Collected {len(businesses)} companies from GitHub")
            return businesses
            
        except Exception as e:
            logger.error(f"Error collecting from GitHub: {e}")
            return []


class EnhancedSampleGenerator:
    """Enhanced sample data generator with more realistic data"""

    def __init__(self):
        """Initialize enhanced sample generator"""
        self.real_business_names = {
            'UAE': [
                "Emirates National Oil Company", "Abu Dhabi Commercial Bank", "Dubai Islamic Bank",
                "Emirates Airlines", "Etihad Airways", "Abu Dhabi National Oil Company",
                "Dubai Electricity and Water Authority", "Abu Dhabi Water and Electricity Authority",
                "Emirates Telecommunications Corporation", "Abu Dhabi Securities Exchange",
                "Dubai Financial Market", "Dubai Gold and Commodities Exchange",
                "Emirates NBD", "First Abu Dhabi Bank", "Abu Dhabi Islamic Bank",
                "Dubai Islamic Insurance", "Abu Dhabi National Insurance Company"
            ],
            'USA': [
                "Microsoft Corporation", "Apple Inc.", "Amazon.com Inc.", "Alphabet Inc.",
                "Meta Platforms Inc.", "Tesla Inc.", "NVIDIA Corporation", "Johnson & Johnson",
                "JPMorgan Chase & Co.", "Bank of America Corporation", "Wells Fargo & Company",
                "Procter & Gamble Company", "UnitedHealth Group Incorporated", "Pfizer Inc.",
                "Chevron Corporation", "Exxon Mobil Corporation", "Home Depot Inc.",
                "Walmart Inc.", "Costco Wholesale Corporation", "Target Corporation"
            ]
        }
        
        self.business_types = [
            "Construction", "Technology", "Healthcare", "Financial Services", "Retail",
            "Manufacturing", "Logistics", "Real Estate", "Consulting", "Education",
            "Hospitality", "Energy", "Telecommunications", "Media", "Agriculture"
        ]
        
        self.uae_cities = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
        self.usa_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        self.usa_states = ["NY", "CA", "IL", "TX", "AZ", "PA", "FL", "CO", "GA", "WA"]

    def generate_realistic_businesses(self, country: str, count: int = 100) -> List[Dict]:
        """
        Generate realistic business data using real company names and patterns
        
        Args:
            country: Country name (UAE or USA)
            count: Number of businesses to generate
            
        Returns:
            List of business data
        """
        import random
        from datetime import datetime, timezone
        
        businesses = []
        
        # Mix of real and generated names
        real_names = self.real_business_names.get(country, [])
        real_names_count = min(len(real_names), count // 4)  # Use real names for 25%
        generated_count = count - real_names_count
        
        # Generate businesses with real names
        for i in range(real_names_count):
            name = real_names[i % len(real_names)]
            business = self._create_business_record(name, country, is_real=True)
            businesses.append(business)
        
        # Generate additional businesses with realistic names
        for i in range(generated_count):
            name = self._generate_realistic_name(country)
            business = self._create_business_record(name, country, is_real=False)
            businesses.append(business)
        
        random.shuffle(businesses)
        return businesses

    def _generate_realistic_name(self, country: str) -> str:
        """Generate a realistic business name"""
        prefixes = {
            'UAE': ["Al", "Emirates", "Gulf", "National", "Abu Dhabi", "Dubai", "Sharjah", "Arabian", "Royal", "Premium"],
            'USA': ["American", "National", "United", "Pacific", "Atlantic", "Central", "Western", "Eastern", "Premier", "Elite"]
        }
        
        suffixes = ["Group", "Corporation", "Company", "Industries", "Enterprises", "International", "Holdings", "Solutions", "Services", "Technologies"]
        
        prefix = random.choice(prefixes.get(country, ["Global"]))
        suffix = random.choice(suffixes)
        business_type = random.choice(self.business_types)
        
        return f"{prefix} {business_type} {suffix}"

    def _create_business_record(self, name: str, country: str, is_real: bool) -> Dict:
        """Create a business record with realistic data"""
        import random
        
        if country == "UAE":
            city = random.choice(self.uae_cities)
            state = city
            phone = f"+971-{random.randint(2,7)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        else:
            city = random.choice(self.usa_cities)
            state = random.choice(self.usa_states)
            phone = f"+1-{random.randint(200,999)}-{random.randint(555,999)}-{random.randint(1000,9999)}"
        
        business_type = random.choice(self.business_types)
        
        # Generate realistic email and website
        simple_name = name.lower().replace(" ", "").replace(".", "").replace(",", "")
        email = f"info@{simple_name}.com"
        website = f"https://www.{simple_name}.com"
        
        return {
            'business_name': name,
            'category': business_type,
            'address': f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Broadway', 'First Ave', 'Park Rd'])}, {city}, {state}",
            'city': city,
            'state': state,
            'country': country,
            'phone': phone,
            'email': email,
            'website': website,
            'rating': round(random.uniform(3.5, 5.0), 1),
            'review_count': random.randint(10, 500) if is_real else random.randint(5, 100),
            'source': 'Enhanced Sample Generator',
            'source_url': website,
            'source_type': 'generated',
            'source_verified': True
        }