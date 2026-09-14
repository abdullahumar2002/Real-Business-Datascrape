"""
Database management for business lead agent
"""

import os
import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from src.models import Base, Business

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_path: str = "data/business.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self._initialize_database()

    def _initialize_database(self):
        """Create database engine and tables"""
        try:
            # Create SQLite engine
            self.engine = create_engine(
                f'sqlite:///{self.db_path}',
                echo=False,
                connect_args={"check_same_thread": False}
            )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Create all tables
            Base.metadata.create_all(bind=self.engine)

            logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions

        Yields:
            Session: SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def add_business(self, business_data: dict) -> Business:
        """
        Add a business to the database

        Args:
            business_data: Dictionary of business fields

        Returns:
            Business: Created business object
        """
        with self.get_session() as session:
            business = Business(**business_data)
            session.add(business)
            session.flush()
            session.refresh(business)
            logger.debug(f"Added business: {business.business_name} (ID: {business.id})")
            return business

    def get_business_by_id(self, business_id: int) -> dict:
        """
        Get a business by ID

        Args:
            business_id: Business ID

        Returns:
            dict: Business dictionary or None
        """
        with self.get_session() as session:
            business = session.query(Business).filter(Business.id == business_id).first()
            if business:
                return business.to_dict()
            return None

    def get_business_by_website(self, website: str) -> Business:
        """
        Get a business by website domain

        Args:
            website: Website URL

        Returns:
            Business: Business object or None
        """
        with self.get_session() as session:
            business = session.query(Business).filter(Business.website == website).first()
            if business:
                # Convert to dict while session is active
                business_dict = business.to_dict()
                return business_dict
            return None

    def get_business_by_phone(self, phone: str) -> Business:
        """
        Get a business by phone number

        Args:
            phone: Phone number

        Returns:
            Business: Business object or None
        """
        with self.get_session() as session:
            business = session.query(Business).filter(Business.phone == phone).first()
            if business:
                # Convert to dict while session is active
                business_dict = business.to_dict()
                return business_dict
            return None

    def get_business_by_email(self, email: str) -> Business:
        """
        Get a business by email

        Args:
            email: Email address

        Returns:
            Business: Business object or None
        """
        with self.get_session() as session:
            business = session.query(Business).filter(Business.email == email).first()
            if business:
                # Convert to dict while session is active
                business_dict = business.to_dict()
                return business_dict
            return None

    def update_business(self, business_id: int, update_data: dict) -> dict:
        """
        Update a business record

        Args:
            business_id: Business ID
            update_data: Dictionary of fields to update

        Returns:
            dict: Updated business dictionary
        """
        with self.get_session() as session:
            business = session.query(Business).filter(Business.id == business_id).first()
            if business:
                for key, value in update_data.items():
                    setattr(business, key, value)
                session.flush()
                session.refresh(business)
                logger.debug(f"Updated business: {business.business_name} (ID: {business.id})")
                return business.to_dict()
            return None

    def get_all_businesses(self, verification_status: str = None) -> list:
        """
        Get all businesses, optionally filtered by verification status

        Args:
            verification_status: Optional filter for verification status

        Returns:
            list: List of Business objects
        """
        with self.get_session() as session:
            query = session.query(Business)
            if verification_status:
                query = query.filter(Business.verification_status == verification_status)
            businesses = query.all()
            # Convert to dict while session is still active
            return [b.to_dict() for b in businesses]

    def get_businesses_by_country(self, country: str) -> list:
        """
        Get businesses by country

        Args:
            country: Country name

        Returns:
            list: List of Business dictionaries
        """
        with self.get_session() as session:
            businesses = session.query(Business).filter(Business.country == country).all()
            return [b.to_dict() for b in businesses]

    def get_statistics(self) -> dict:
        """
        Get database statistics

        Returns:
            dict: Statistics dictionary
        """
        with self.get_session() as session:
            total = session.query(func.count(Business.id)).scalar()

            by_country = session.query(
                Business.country,
                func.count(Business.id)
            ).group_by(Business.country).all()

            by_status = session.query(
                Business.verification_status,
                func.count(Business.id)
            ).group_by(Business.verification_status).all()

            websites_checked = session.query(func.count(Business.id)).filter(
                Business.website_status.isnot(None)
            ).scalar()

            working_websites = session.query(func.count(Business.id)).filter(
                Business.website_status == 'working'
            ).scalar()

            public_emails = session.query(func.count(Business.id)).filter(
                Business.email.isnot(None)
            ).scalar()

            public_phones = session.query(func.count(Business.id)).filter(
                Business.phone.isnot(None)
            ).scalar()

            duplicates = session.query(func.count(Business.id)).filter(
                Business.duplicate == 'true'
            ).scalar()

            rejected = session.query(func.count(Business.id)).filter(
                Business.verification_status == 'REJECTED'
            ).scalar()

            return {
                'total': total,
                'by_country': dict(by_country),
                'by_status': dict(by_status),
                'websites_checked': websites_checked,
                'working_websites': working_websites,
                'public_emails': public_emails,
                'public_phones': public_phones,
                'duplicates': duplicates,
                'rejected': rejected,
            }

    def get_leads_by_priority(self, priority: str) -> list:
        """
        Get leads by priority level

        Args:
            priority: Priority level (high, medium, low)

        Returns:
            list: List of Business dictionaries
        """
        with self.get_session() as session:
            businesses = session.query(Business).filter(
                Business.lead_priority == priority
            ).all()
            return [b.to_dict() for b in businesses]

    def get_businesses_without_website(self) -> list:
        """
        Get businesses without a website

        Returns:
            list: List of Business dictionaries
        """
        with self.get_session() as session:
            businesses = session.query(Business).filter(
                (Business.website.is_(None)) | (Business.website == '')
            ).all()
            return [b.to_dict() for b in businesses]

    def get_non_duplicate_businesses(self) -> list:
        """
        Get non-duplicate businesses

        Returns:
            list: List of Business dictionaries
        """
        with self.get_session() as session:
            businesses = session.query(Business).filter(
                (Business.duplicate != 'true') | (Business.duplicate.is_(None))
            ).all()
            return [b.to_dict() for b in businesses]
