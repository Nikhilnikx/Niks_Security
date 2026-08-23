import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class PlanType(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    plan = Column(SAEnum(PlanType), default=PlanType.FREE, nullable=False)
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Plan limits
    max_users = Column(Integer, default=5, nullable=False)
    max_assets = Column(Integer, default=10, nullable=False)
    max_events_per_day = Column(Integer, default=10000, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)

    # Relationships
    members = relationship("User", back_populates="organization")
    assets = relationship("Asset", back_populates="organization")
    security_events = relationship("SecurityEvent", back_populates="organization")
    alerts = relationship("Alert", back_populates="organization")
    incidents = relationship("Incident", back_populates="organization")
    detection_rules = relationship("DetectionRule", back_populates="organization")
    threat_indicators = relationship("ThreatIndicator", back_populates="organization")
    reports = relationship("Report", back_populates="organization")


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    organization_id = Column(Integer, nullable=False, index=True)
    role = Column(String(20), default="viewer", nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
