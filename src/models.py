"""
Database models for business lead agent
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class Business(Base):
    """
    Business model with complete verification and traceability fields
    """
    __tablename__ = 'businesses'

    # Primary identifiers
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic business information
    business_name = Column(String(500), nullable=False, index=True)
    category = Column(String(200), nullable=True, index=True)
    subcategory = Column(String(200), nullable=True)

    # Location information
    country = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=True)
    city = Column(String(200), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    postal_code = Column(String(50), nullable=True)

    # Contact information
    phone = Column(String(100), nullable=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    website = Column(String(500), nullable=True, index=True)

    # Ratings and reviews
    rating = Column(Float, nullable=True)
    review_count = Column(Integer, nullable=True)

    # Source traceability
    source = Column(String(200), nullable=False, index=True)
    source_url = Column(String(1000), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_verified = Column(Boolean, default=False, nullable=False)

    # Directory vs Official contact info
    directory_email = Column(String(255), nullable=True)
    directory_phone = Column(String(100), nullable=True)
    official_email = Column(String(255), nullable=True)
    official_phone = Column(String(100), nullable=True)
    official_address = Column(String(500), nullable=True)

    # Website verification
    website_status = Column(String(50), nullable=True)  # working, unreachable, timeout, error
    website_verified = Column(Boolean, default=False, nullable=False)
    website_business_match = Column(Boolean, default=False, nullable=False)
    https_enabled = Column(Boolean, nullable=True)
    mobile_viewport = Column(Boolean, nullable=True)
    contact_page_found = Column(Boolean, nullable=True)
    social_links_found = Column(Boolean, nullable=True)
    website_title = Column(String(500), nullable=True)
    website_quality_score = Column(Integer, nullable=True)

    # Deduplication
    duplicate = Column(String(20), nullable=True, index=True)  # true, false, possible
    duplicate_of = Column(Integer, nullable=True)

    # Verification status
    verification_status = Column(String(50), nullable=False, index=True, default='PENDING')
    # DIRECTORY_ONLY, DIRECTORY_PLUS_WEBSITE, WEBSITE_VERIFIED, MULTI_SOURCE_VERIFIED, REJECTED
    verification_notes = Column(Text, nullable=True)

    # Lead scoring
    lead_score = Column(Integer, nullable=True, index=True)
    lead_priority = Column(String(20), nullable=True, index=True)  # high, medium, low
    lead_reason = Column(Text, nullable=True)

    # Timestamps
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    verified_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.business_name}', country='{self.country}')>"

    def to_dict(self):
        """Convert business to dictionary for export"""
        return {
            'id': self.id,
            'business_name': self.business_name,
            'category': self.category,
            'subcategory': self.subcategory,
            'country': self.country,
            'state': self.state,
            'city': self.city,
            'address': self.address,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'rating': self.rating,
            'review_count': self.review_count,
            'source': self.source,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'source_verified': self.source_verified,
            'directory_email': self.directory_email,
            'directory_phone': self.directory_phone,
            'official_email': self.official_email,
            'official_phone': self.official_phone,
            'official_address': self.official_address,
            'website_status': self.website_status,
            'website_verified': self.website_verified,
            'website_business_match': self.website_business_match,
            'https_enabled': self.https_enabled,
            'mobile_viewport': self.mobile_viewport,
            'contact_page_found': self.contact_page_found,
            'social_links_found': self.social_links_found,
            'website_title': self.website_title,
            'website_quality_score': self.website_quality_score,
            'duplicate': self.duplicate,
            'duplicate_of': self.duplicate_of,
            'verification_status': self.verification_status,
            'verification_notes': self.verification_notes,
            'lead_score': self.lead_score,
            'lead_priority': self.lead_priority,
            'lead_reason': self.lead_reason,
            'collected_at': self.collected_at.isoformat() if self.collected_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
        }
