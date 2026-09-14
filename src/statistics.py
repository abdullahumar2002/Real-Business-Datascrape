"""
Statistics and reporting utilities
"""

import logging
from typing import Dict, List
from src.database import DatabaseManager

logger = logging.getLogger(__name__)


class Statistics:
    """Statistics and reporting utilities"""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize statistics

        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager

    def get_full_report(self) -> Dict:
        """
        Get comprehensive statistics report

        Returns:
            Dictionary with full statistics
        """
        base_stats = self.db_manager.get_statistics()

        # Additional statistics - businesses are already dictionaries from get_all_businesses
        all_businesses = self.db_manager.get_all_businesses()
        business_dicts = all_businesses

        # Verification status breakdown
        verification_breakdown = {}
        for business_dict in business_dicts:
            status = business_dict.get('verification_status')
            verification_breakdown[status] = verification_breakdown.get(status, 0) + 1

        # Lead priority breakdown
        priority_breakdown = {}
        for business_dict in business_dicts:
            priority = business_dict.get('lead_priority') or 'unknown'
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1

        # Category breakdown
        category_breakdown = {}
        for business_dict in business_dicts:
            category = business_dict.get('category') or 'Unknown'
            category_breakdown[category] = category_breakdown.get(category, 0) + 1

        # Website status breakdown
        website_status_breakdown = {}
        for business_dict in business_dicts:
            status = business_dict.get('website_status') or 'unknown'
            website_status_breakdown[status] = website_status_breakdown.get(status, 0) + 1

        full_report = {
            **base_stats,
            'verification_breakdown': verification_breakdown,
            'priority_breakdown': priority_breakdown,
            'category_breakdown': category_breakdown,
            'website_status_breakdown': website_status_breakdown,
        }

        return full_report

    def print_progress(self, target: int, uae_target: int, usa_target: int):
        """
        Print progress bar and statistics

        Args:
            target: Total target
            uae_target: UAE target
            usa_target: USA target
        """
        stats = self.db_manager.get_statistics()

        uae_count = stats['by_country'].get('UAE', 0)
        usa_count = stats['by_country'].get('USA', 0)
        total = stats['total']

        # Progress bars
        uae_progress = self._create_progress_bar(uae_count, uae_target)
        usa_progress = self._create_progress_bar(usa_count, usa_target)
        total_progress = self._create_progress_bar(total, target)

        print("\n" + "="*50)
        print("PROGRESS")
        print("="*50)
        print(f"\nUAE")
        print(f"{uae_progress} {uae_count} / {uae_target}")
        print(f"\nUSA")
        print(f"{usa_progress} {usa_count} / {usa_target}")
        print(f"\nTOTAL")
        print(f"{total_progress} {total} / {target}")

        # Verification statistics
        print("\n" + "-"*50)
        print("VERIFICATION")
        print("-"*50)
        print(f"\nVerified: {total - stats['duplicates'] - stats['rejected']}")
        print(f"Duplicates: {stats['duplicates']}")
        print(f"Rejected: {stats['rejected']}")
        print(f"Websites checked: {stats['websites_checked']}")
        print(f"Working websites: {stats['working_websites']}")
        print(f"Public emails: {stats['public_emails']}")
        print(f"Public phones: {stats['public_phones']}")

    def _create_progress_bar(self, current: int, target: int, width: int = 20) -> str:
        """
        Create a text progress bar

        Args:
            current: Current progress
            target: Target value
            width: Width of progress bar

        Returns:
            Progress bar string
        """
        if target == 0:
            return '[' + ' ' * width + ']'

        filled = int((current / target) * width)
        filled = min(filled, width)
        bar = '[' + '█' * filled + ' ' * (width - filled) + ']'
        return bar

    def print_final_summary(self, target: int):
        """
        Print final summary

        Args:
            target: Target number of businesses
        """
        stats = self.db_manager.get_statistics()
        all_businesses = self.db_manager.get_all_businesses()

        # businesses are already dictionaries from get_all_businesses
        business_dicts = all_businesses

        # Count verified businesses
        verified_count = len([b for b in business_dicts
                            if b.get('verification_status') in ['WEBSITE_VERIFIED', 'MULTI_SOURCE_VERIFIED']
                            and b.get('duplicate') != 'true'])

        # Count leads by priority
        high_priority = len([b for b in business_dicts
                           if b.get('lead_priority') == 'high' and b.get('duplicate') != 'true'])
        medium_priority = len([b for b in business_dicts
                              if b.get('lead_priority') == 'medium' and b.get('duplicate') != 'true'])
        low_priority = len([b for b in business_dicts
                           if b.get('lead_priority') == 'low' and b.get('duplicate') != 'true'])

        print("\n" + "="*50)
        print("VERIFIED BUSINESS LEAD AGENT")
        print("="*50)

        print(f"\nTarget: {target}")
        print(f"\nVerified: {verified_count}")
        print(f"Duplicates removed: {stats['duplicates']}")
        print(f"Rejected records: {stats['rejected']}")

        print("\n" + "-"*50)
        print("VERIFICATION")
        print("-"*50)
        print(f"\nUnique businesses: {verified_count}")
        print(f"Websites checked: {stats['websites_checked']}")
        print(f"Working websites: {stats['working_websites']}")
        print(f"Public emails: {stats['public_emails']}")
        print(f"Public phones: {stats['public_phones']}")

        print("\n" + "-"*50)
        print("LEAD QUALITY")
        print("-"*50)
        print(f"\nHigh priority: {high_priority}")
        print(f"Medium priority: {medium_priority}")
        print(f"Low priority: {low_priority}")

        print("\n" + "="*50)
        print("COMPLETE")
        print("="*50)
