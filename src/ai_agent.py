"""
AI agent for classification and analysis tasks using LLM
"""

import logging
import json
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class AIAgent:
    """AI agent for classification and analysis tasks"""

    def __init__(self, config: Dict = None):
        """
        Initialize AI agent

        Args:
            config: AI configuration dictionary
        """
        load_dotenv()
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.config = config or {}
        self.provider = self.config.get('provider', 'openai')
        self.model = self.config.get('model', 'gpt-3.5-turbo')
        self.temperature = self.config.get('temperature', 0.3)
        self.max_tokens = self.config.get('max_tokens', 500)

        if not self.api_key:
            logger.warning("OpenAI API key not found. AI features will use rule-based fallbacks.")

    def _is_available(self) -> bool:
        """Check if AI agent is available"""
        return self.api_key is not None

    def classify_category(self, business_name: str, description: str = None) -> Optional[str]:
        """
        Classify business category using AI

        Args:
            business_name: Business name
            description: Optional business description

        Returns:
            Classified category or None
        """
        if not self._is_available():
            return self._rule_based_category(business_name, description)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            prompt = f"""Classify the following business into one of these categories:
Restaurants, Hotels, Real estate, Construction, Interior design, Law firms, Accounting,
Clinics, Dental, Logistics, Automotive, Manufacturing, Retail, Education, Consulting,
Professional services, Beauty, Fitness, Travel, Cleaning, Home services, Other

Business: {business_name}
{f'Description: {description}' if description else ''}

Return only the category name."""

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            category = response.choices[0].message.content.strip()
            logger.debug(f"AI classified {business_name} as {category}")
            return category

        except Exception as e:
            logger.error(f"AI classification failed: {e}, using rule-based fallback")
            return self._rule_based_category(business_name, description)

    def normalize_business_name(self, business_name: str) -> str:
        """
        Normalize business name using AI

        Args:
            business_name: Business name to normalize

        Returns:
            Normalized business name
        """
        if not self._is_available():
            from src.normalizer import DataNormalizer
            return DataNormalizer.normalize_business_name(business_name) or business_name

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            prompt = f"""Normalize this business name to a standard format:
- Remove LLC, Inc, Ltd, Corp, etc. suffixes
- Use title case
- Remove extra spaces
- Keep the core business name

Business: {business_name}

Return only the normalized name."""

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            normalized = response.choices[0].message.content.strip()
            logger.debug(f"AI normalized {business_name} to {normalized}")
            return normalized

        except Exception as e:
            logger.error(f"AI normalization failed: {e}, using rule-based fallback")
            from src.normalizer import DataNormalizer
            return DataNormalizer.normalize_business_name(business_name) or business_name

    def detect_duplicate_probability(self, business1: Dict, business2: Dict) -> float:
        """
        Detect probability that two businesses are duplicates using AI

        Args:
            business1: First business data
            business2: Second business data

        Returns:
            Probability score (0-1)
        """
        if not self._is_available():
            return self._rule_based_duplicate_probability(business1, business2)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            prompt = f"""Determine the probability (0.0 to 1.0) that these two businesses are the same:

Business 1:
Name: {business1.get('business_name')}
City: {business1.get('city')}
Phone: {business1.get('phone')}
Website: {business1.get('website')}

Business 2:
Name: {business2.get('business_name')}
City: {business2.get('city')}
Phone: {business2.get('phone')}
Website: {business2.get('website')}

Consider:
- Similar business names
- Same city/location
- Same phone number
- Same website
- Same category

Return only a number between 0.0 and 1.0."""

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            probability_str = response.choices[0].message.content.strip()
            try:
                probability = float(probability_str)
                logger.debug(f"AI duplicate probability: {probability}")
                return max(0.0, min(1.0, probability))
            except ValueError:
                logger.warning(f"AI returned invalid probability: {probability_str}")
                return self._rule_based_duplicate_probability(business1, business2)

        except Exception as e:
            logger.error(f"AI duplicate detection failed: {e}, using rule-based fallback")
            return self._rule_based_duplicate_probability(business1, business2)

    def analyze_lead_quality(self, business_data: Dict) -> Dict:
        """
        Analyze lead quality using AI

        Args:
            business_data: Business data dictionary

        Returns:
            Dictionary with lead quality analysis
        """
        if not self._is_available():
            return self._rule_based_lead_analysis(business_data)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            prompt = f"""Analyze this business as a potential digital services lead:
Name: {business_data.get('business_name')}
Category: {business_data.get('category')}
Website: {business_data.get('website')}
Website Status: {business_data.get('website_status')}
Email: {business_data.get('email')}
Phone: {business_data.get('phone')}
Rating: {business_data.get('rating')}
Reviews: {business_data.get('review_count')}

Provide JSON response with:
{{
  "priority": "high" or "medium" or "low",
  "reason": "brief explanation",
  "needs_website": true or false,
  "needs_digital_upgrade": true or false
}}"""

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            result_str = response.choices[0].message.content.strip()
            try:
                result = json.loads(result_str)
                logger.debug(f"AI lead analysis: {result}")
                return result
            except json.JSONDecodeError:
                logger.warning(f"AI returned invalid JSON: {result_str}")
                return self._rule_based_lead_analysis(business_data)

        except Exception as e:
            logger.error(f"AI lead analysis failed: {e}, using rule-based fallback")
            return self._rule_based_lead_analysis(business_data)

    def _rule_based_category(self, business_name: str, description: str = None) -> Optional[str]:
        """Rule-based category classification fallback"""
        business_lower = business_name.lower()
        desc_lower = description.lower() if description else ""

        category_keywords = {
            'Restaurants': ['restaurant', 'cafe', 'food', 'pizza', 'sushi', 'bar', 'grill'],
            'Hotels': ['hotel', 'motel', 'resort', 'inn', 'lodge'],
            'Real estate': ['real estate', 'property', 'apartment', 'rental'],
            'Construction': ['construction', 'builder', 'contractor'],
            'Interior design': ['interior', 'design', 'decor'],
            'Law firms': ['law', 'legal', 'attorney', 'lawyer'],
            'Accounting': ['accounting', 'accountant', 'tax', 'audit'],
            'Clinics': ['clinic', 'medical', 'health'],
            'Dental': ['dental', 'dentist', 'orthodontist'],
            'Logistics': ['logistics', 'shipping', 'transport', 'delivery'],
            'Automotive': ['auto', 'car', 'mechanic', 'dealer'],
            'Manufacturing': ['manufacturing', 'factory', 'production'],
            'Retail': ['retail', 'store', 'shop', 'market'],
            'Education': ['education', 'school', 'training', 'university'],
            'Consulting': ['consulting', 'consultant'],
            'Professional services': ['services', 'agency', 'firm'],
            'Beauty': ['beauty', 'salon', 'spa', 'cosmetic'],
            'Fitness': ['fitness', 'gym', 'health club'],
            'Travel': ['travel', 'tour', 'agency'],
            'Cleaning': ['cleaning', 'janitorial', 'maid'],
            'Home services': ['home', 'repair', 'maintenance', 'plumbing', 'electrical'],
        }

        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in business_lower or keyword in desc_lower:
                    return category

        return 'Other'

    def _rule_based_duplicate_probability(self, business1: Dict, business2: Dict) -> float:
        """Rule-based duplicate detection fallback"""
        from src.normalizer import DataNormalizer

        score = 0.0

        # Check website
        if business1.get('website') and business2.get('website'):
            w1 = DataNormalizer.extract_domain(business1['website'])
            w2 = DataNormalizer.extract_domain(business2['website'])
            if w1 and w2 and w1 == w2:
                score += 0.5

        # Check phone
        if business1.get('phone') and business2.get('phone'):
            p1 = DataNormalizer.normalize_phone(business1['phone'])
            p2 = DataNormalizer.normalize_phone(business2['phone'])
            if p1 and p2 and p1 == p2:
                score += 0.4

        # Check email
        if business1.get('email') and business2.get('email'):
            e1 = DataNormalizer.normalize_email(business1['email'])
            e2 = DataNormalizer.normalize_email(business2['email'])
            if e1 and e2 and e1 == e2:
                score += 0.3

        # Check name similarity
        if business1.get('business_name') and business2.get('business_name'):
            if DataNormalizer.are_similar_names(
                business1['business_name'],
                business2['business_name']
            ):
                score += 0.2

        # Check city
        if business1.get('city') and business2.get('city'):
            c1 = DataNormalizer.normalize_city(business1['city'])
            c2 = DataNormalizer.normalize_city(business2['city'])
            if c1 and c2 and c1 == c2:
                score += 0.1

        return min(1.0, score)

    def _rule_based_lead_analysis(self, business_data: Dict) -> Dict:
        """Rule-based lead analysis fallback"""
        priority = 'low'
        reason = ''
        needs_website = False
        needs_digital_upgrade = False

        # Check for website
        if not business_data.get('website'):
            needs_website = True
            priority = 'high'
            reason = 'No website - potential digital services lead'
        elif business_data.get('website_status') != 'working':
            needs_digital_upgrade = True
            priority = 'high'
            reason = 'Website not working - needs attention'
        elif business_data.get('website_quality_score', 0) < 50:
            needs_digital_upgrade = True
            priority = 'medium'
            reason = 'Low website quality score'

        # Check contact information
        if not business_data.get('email') and not business_data.get('phone'):
            if priority == 'low':
                priority = 'medium'
                reason = 'Missing contact information'

        # Check established business
        if business_data.get('review_count', 0) > 10 or business_data.get('rating', 0) > 4.0:
            if priority == 'low':
                priority = 'medium'
                reason = 'Established business with reviews'

        return {
            'priority': priority,
            'reason': reason,
            'needs_website': needs_website,
            'needs_digital_upgrade': needs_digital_upgrade
        }
