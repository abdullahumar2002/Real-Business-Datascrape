#!/usr/bin/env python3
"""
Business Lead Agent - Main CLI Interface
AI-powered business research and verification system
"""

import argparse
import logging
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from src.database import DatabaseManager
from src.models import Business
from src.source_manager import SourceManager
from src.robots import RobotsChecker
from src.crawler import Crawler
from src.parser import BusinessParser
from src.normalizer import DataNormalizer
from src.website_checker import WebsiteChecker
from src.deduplicator import Deduplicator
from src.ai_agent import AIAgent
from src.lead_scoring import LeadScorer
from src.csv_importer import CSVImporter
from src.exporters import DataExporter
from src.pdf_report import PDFReportGenerator
from src.statistics import Statistics
from src.data_collector import MultiSourceDataCollector

# Setup logging
def setup_logging(log_file: str = "logs/agent.log", log_level: str = "INFO"):
    """Setup logging configuration"""
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class BusinessLeadAgent:
    """Main agent class that orchestrates all components"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the agent"""
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize components
        self.db_manager = DatabaseManager(
            self.config['database']['path']
        )

        self.source_manager = SourceManager("config/sources.yaml")
        self.robots_checker = RobotsChecker()

        self.crawler = Crawler(
            delay_min=self.config['rate_limiting']['delay_min'],
            delay_max=self.config['rate_limiting']['delay_max'],
            timeout=self.config['rate_limiting']['timeout'],
            max_retries=self.config['rate_limiting']['max_retries']
        )

        self.website_checker = WebsiteChecker(self.crawler)
        self.deduplicator = Deduplicator(self.db_manager)

        # Initialize AI agent
        self.ai_agent = AIAgent(self.config.get('ai', {}))

        # Initialize lead scorer
        self.lead_scorer = LeadScorer(
            self.config.get('lead_scoring', {}),
            self.ai_agent
        )

        # Initialize exporters
        self.exporter = DataExporter(
            self.db_manager,
            self.config['output']['directory']
        )

        self.pdf_generator = PDFReportGenerator(
            self.db_manager,
            self.config['output']['directory']
        )

        self.statistics = Statistics(self.db_manager)

        # Initialize multi-source data collector
        self.data_collector = MultiSourceDataCollector(self.db_manager, self.crawler)

        logger.info("Business Lead Agent initialized")

    def run(self, target: int = 500, country: str = None, resume: bool = False):
        """
        Run the main agent process

        Args:
            target: Target number of businesses
            country: Optional country filter (UAE, USA)
            resume: Whether to resume from existing data
        """
        logger.info(f"Starting agent with target: {target}")

        # Calculate country targets
        if country:
            if country.upper() == 'UAE':
                uae_target = target
                usa_target = 0
            elif country.upper() == 'USA':
                uae_target = 0
                usa_target = target
            else:
                logger.error(f"Invalid country: {country}")
                return
        else:
            uae_target = target // 2
            usa_target = target - uae_target

        # Check for existing data if resuming
        if resume:
            stats = self.db_manager.get_statistics()
            logger.info(f"Resuming from existing data: {stats['total']} records")
        else:
            # Optionally clear existing data for fresh start
            # This is commented out to preserve data by default
            # self._clear_database()
            pass

        # Process sources using multi-source data collector
        if country:
            countries = [country.upper()]
        else:
            countries = ['UAE', 'USA']
        
        logger.info(f"Starting multi-source data collection for: {countries}")
        collection_stats = self.data_collector.collect_businesses(target, countries)
        logger.info(f"Data collection stats: {collection_stats}")

        # Run deduplication
        logger.info("Running deduplication")
        dedup_stats = self.deduplicator.run_deduplication()

        # Score leads
        logger.info("Scoring leads")
        self._score_all_leads()

        # Export results
        logger.info("Exporting results")
        self._export_all()

        # Print final summary
        self.statistics.print_final_summary(target)

    def _process_country(self, country: str, target: int):
        """
        Process businesses for a specific country

        Args:
            country: Country name
            target: Target number of businesses
        """
        logger.info(f"Processing {country} businesses, target: {target}")

        # Get current count
        stats = self.db_manager.get_statistics()
        current_count = stats['by_country'].get(country, 0)

        if current_count >= target:
            logger.info(f"Already have {current_count} {country} businesses, skipping")
            return

        needed = target - current_count
        logger.info(f"Need {needed} more {country} businesses")

        # Get allowed sources for this country
        sources = self.source_manager.get_allowed_sources_by_country(country)

        if not sources:
            logger.warning(f"No allowed sources found for {country}")
            logger.info("Use --import-csv to import data from CSV file")
            return

        # Process each source
        for source in sources:
            if needed <= 0:
                break

            logger.info(f"Processing source: {source['name']}")

            # Check if automation is allowed
            allowed, status = self.robots_checker.is_automation_allowed(source)
            if not allowed:
                logger.warning(f"Source not allowed for automation: {status}")
                continue

            # Process source (this would be implemented per source type)
            # For now, this is a placeholder - actual scraping would go here
            collected = self._process_source(source, needed)
            needed -= collected

            # Update progress
            self.statistics.print_progress(
                self.config['targets']['total'],
                self.config['targets']['uae'],
                self.config['targets']['usa']
            )

    def _process_source(self, source: dict, needed: int) -> int:
        """
        Process a single source (placeholder for actual implementation)

        Args:
            source: Source configuration
            needed: Number of businesses needed

        Returns:
            Number of businesses collected
        """
        # This is a placeholder - actual scraping implementation would go here
        # For now, we return 0 since we don't have actual scrapable sources configured
        logger.info(f"Source processing not implemented for: {source['name']}")
        logger.info("Use --import-csv to import data from CSV file")
        return 0

    def _score_all_leads(self):
        """Score all businesses as leads"""
        businesses = self.db_manager.get_all_businesses()

        # businesses are already dictionaries from get_all_businesses
        business_dicts = businesses

        for business_dict in business_dicts:
            if business_dict.get('duplicate') != 'true' and not business_dict.get('lead_score'):
                score_data = self.lead_scorer.score_business(business_dict)

                self.db_manager.update_business(business_dict['id'], score_data)

    def _export_all(self):
        """Export all formats"""
        output_config = self.config['output']

        # CSV
        csv_path = self.exporter.export_csv(output_config['csv_filename'])
        logger.info(f"CSV exported: {csv_path}")

        # Excel
        excel_path = self.exporter.export_excel(output_config['excel_filename'])
        logger.info(f"Excel exported: {excel_path}")

        # JSON
        json_path = self.exporter.export_json(output_config['json_filename'])
        logger.info(f"JSON exported: {json_path}")

        # PDF
        pdf_path = self.pdf_generator.generate_pdf(output_config['pdf_filename'])
        logger.info(f"PDF exported: {pdf_path}")

        # Verification report
        report_path = self.exporter.export_verification_report(output_config['report_filename'])
        logger.info(f"Verification report exported: {report_path}")

    def import_csv(self, csv_path: str):
        """
        Import businesses from CSV file

        Args:
            csv_path: Path to CSV file
        """
        logger.info(f"Importing CSV: {csv_path}")

        importer = CSVImporter(self.db_manager)

        # Validate CSV structure
        if not importer.validate_csv_structure(csv_path):
            logger.error("Invalid CSV structure")
            return

        # Import
        stats = importer.import_csv(csv_path)
        logger.info(f"Import complete: {stats}")

    def verify_existing(self):
        """Verify existing businesses in database"""
        logger.info("Verifying existing businesses")

        businesses = self.db_manager.get_all_businesses()

        # businesses are already dictionaries from get_all_businesses
        business_dicts = businesses

        for business_dict in business_dicts:
            if business_dict.get('website') and not business_dict.get('website_verified'):
                logger.info(f"Verifying website for: {business_dict.get('business_name')}")

                website_data = self.website_checker.check_website(
                    business_dict['website'],
                    business_dict['business_name']
                )

                self.db_manager.update_business(business_dict['id'], website_data)

                # Update verification status
                if website_data['website_verified']:
                    verification_status = 'WEBSITE_VERIFIED'
                else:
                    verification_status = 'DIRECTORY_ONLY'

                self.db_manager.update_business(business_dict['id'], {
                    'verification_status': verification_status,
                    'verified_at': datetime.now(timezone.utc)
                })

    def export_only(self):
        """Export existing data without collecting new data"""
        logger.info("Exporting existing data")
        self._export_all()

    def generate_pdf_only(self):
        """Generate PDF report only"""
        logger.info("Generating PDF report")
        output_config = self.config['output']
        pdf_path = self.pdf_generator.generate_pdf(output_config['pdf_filename'])
        logger.info(f"PDF generated: {pdf_path}")

    def show_stats(self):
        """Show statistics"""
        logger.info("Showing statistics")
        stats = self.statistics.get_full_report()
        print("\n=== Statistics ===")
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"\n{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")

    def _clear_database(self):
        """Clear all data from database (use with caution)"""
        logger.warning("Clearing database")
        with self.db_manager.get_session() as session:
            session.query(Business).delete()
            session.commit()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Business Lead Agent - AI-powered business research and verification'
    )

    parser.add_argument('--target', type=int, default=500,
                       help='Target number of businesses (default: 500)')
    parser.add_argument('--country', type=str, choices=['UAE', 'USA'],
                       help='Specific country to process')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing data')
    parser.add_argument('--verify', action='store_true',
                       help='Verify existing businesses')
    parser.add_argument('--export', action='store_true',
                       help='Export existing data')
    parser.add_argument('--import-csv', type=str,
                       help='Import businesses from CSV file')
    parser.add_argument('--pdf', action='store_true',
                       help='Generate PDF report')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics')
    parser.add_argument('--collect', action='store_true',
                       help='Start multi-source data collection')
    parser.add_argument('--config', type=str, default='config/settings.yaml',
                       help='Path to configuration file')

    args = parser.parse_args()

    # Setup logging
    setup_logging(
        log_file="logs/agent.log",
        log_level="INFO"
    )

    try:
        # Initialize agent
        agent = BusinessLeadAgent(args.config)

        # Execute command
        if args.import_csv:
            agent.import_csv(args.import_csv)
        elif args.verify:
            agent.verify_existing()
        elif args.export:
            agent.export_only()
        elif args.pdf:
            agent.generate_pdf_only()
        elif args.stats:
            agent.show_stats()
        elif args.collect:
            # Start multi-source data collection
            countries = [args.country] if args.country else ['UAE', 'USA']
            collection_stats = agent.data_collector.collect_businesses(args.target, countries)
            logger.info(f"Data collection completed: {collection_stats}")
        else:
            # Default: run full process
            agent.run(
                target=args.target,
                country=args.country,
                resume=args.resume
            )

    except Exception as e:
        logger.error(f"Agent failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
