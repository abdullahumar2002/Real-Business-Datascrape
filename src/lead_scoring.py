"""
Lead scoring system for evaluating business digital-service potential
"""

import logging
from typing import Dict, Optional
from src.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class LeadScorer:
    """Scores businesses as potential digital-service leads"""

    def __init__(self, config: Dict = None, ai_agent: AIAgent = None):
        """
        Initialize lead scorer

        Args:
            config: Lead scoring configuration
            ai_agent: AI agent for enhanced analysis
        """
        self.config = config or {}
        self.ai_agent = ai_agent

        # Default scoring weights
        self.weights = {
            'no_website': self.config.get('no_website', 20),
            'outdated_website': self.config.get('outdated_website', 15),
            'unreachable_website': self.config.get('unreachable_website', 15),
            'weak_online_presence': self.config.get('weak_online_presence', 10),
            'has_public_email': self.config.get('has_public_email', 10),
            'has_public_phone': self.config.get('has_public_phone', 10),
            'established_local': self.config.get('established_local', 10),
            'many_reviews': self.config.get('many_reviews', 5),
            'high_value_category': self.config.get('high_value_category', 5),
        }

        self.high_value_categories = set(
            self.config.get('high_value_categories', [
                'Restaurants', 'Hotels', 'Real estate', 'Construction',
                'Interior design', 'Law firms', 'Accounting', 'Clinics',
                'Dental', 'Logistics', 'Automotive', 'Manufacturing',
                'Retail', 'Education', 'Consulting', 'Professional services',
                'Beauty', 'Fitness', 'Travel', 'Cleaning', 'Home services'
            ])
        )

    def score_business(self, business_data: Dict) -> Dict:
        """
        Score a business as a potential lead

        Args:
            business_data: Business data dictionary

        Returns:
            Dictionary with score and priority
        """
        score = 0
        reasons = []

        # Check for website
        if not business_data.get('website'):
            score += self.weights['no_website']
            reasons.append('No website')
        elif business_data.get('website_status') == 'unreachable':
            score += self.weights['unreachable_website']
            reasons.append('Website unreachable')
        elif business_data.get('website_quality_score', 100) < 50:
            score += self.weights['outdated_website']
            reasons.append('Low website quality')

        # Check online presence
        if not business_data.get('website') and not business_data.get('email'):
            score += self.weights['weak_online_presence']
            reasons.append('Weak online presence')

        # Check contact information
        if business_data.get('email'):
            score += self.weights['has_public_email']
            reasons.append('Has public email')

        if business_data.get('phone'):
            score += self.weights['has_public_phone']
            reasons.append('Has public phone')

        # Check if established local business
        if self._is_established_local(business_data):
            score += self.weights['established_local']
            reasons.append('Established local business')

        # Check reviews
        if business_data.get('review_count', 0) > 10:
            score += self.weights['many_reviews']
            reasons.append('Many reviews')

        # Check category
        if business_data.get('category') in self.high_value_categories:
            score += self.weights['high_value_category']
            reasons.append('High-value category')

        # Use AI for enhanced analysis if available
        if self.ai_agent:
            try:
                ai_analysis = self.ai_agent.analyze_lead_quality(business_data)
                # Adjust score based on AI analysis
                if ai_analysis.get('priority') == 'high':
                    score = max(score, 70)
                elif ai_analysis.get('priority') == 'medium':
                    score = max(score, 40)
                reasons.append(f"AI: {ai_analysis.get('reason', '')}")
            except Exception as e:
                logger.warning(f"AI lead analysis failed: {e}")

        # Determine priority
        priority = self._determine_priority(score)

        return {
            'lead_score': min(100, score),
            'lead_priority': priority,
            'lead_reason': '; '.join(reasons) if reasons else 'General business'
        }

    def _is_established_local(self, business_data: Dict) -> bool:
        """Check if business appears to be an established local business"""
        # Has physical address
        if business_data.get('address'):
            return True

        # Has reviews
        if business_data.get('review_count', 0) > 0:
            return True

        # Has rating
        if business_data.get('rating', 0) > 0:
            return True

        # In local directory
        if business_data.get('source_type') == 'directory':
            return True

        return False

    def _determine_priority(self, score: int) -> str:
        """Determine priority level from score"""
        if score >= 70:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'

    def batch_score(self, businesses: list) -> list:
        """
        Score multiple businesses

        Args:
            businesses: List of business data dictionaries or Business objects

        Returns:
            List of businesses with scores added
        """
        scored_businesses = []
        for business in businesses:
            # Convert to dict if it's a Business object (while session is active)
            if hasattr(business, 'to_dict'):
                business_dict = business.to_dict()
            else:
                business_dict = business

            score_data = self.score_business(business_dict)
            business_dict.update(score_data)
            scored_businesses.append(business_dict)

        return scored_businesses
