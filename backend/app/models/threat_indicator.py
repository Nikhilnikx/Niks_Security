from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class ThreatIndicator(Base):
    __tablename__ = "threat_indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(String(20), nullable=False, index=True)  # ip, domain, url, hash, user_agent
    value = Column(String(500), nullable=False, index=True)
    threat_type = Column(String(100), nullable=True)
    severity = Column(String(20), default="low", nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False)
    reputation = Column(String(50), nullable=True)  # malicious, suspicious, clean, unknown
    geolocation = Column(String(100), nullable=True)
    asn = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(200), nullable=True)  # where the intel came from
    is_active = Column(Boolean, default=True, nullable=False)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    detection_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="threat_indicators")

    def to_dict(self):
        return {
            "id": self.id,
            "indicator_type": self.indicator_type,
            "value": self.value,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "reputation": self.reputation,
            "geolocation": self.geolocation,
            "asn": self.asn,
            "country": self.country,
            "description": self.description,
            "source": self.source,
            "is_active": self.is_active,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "detection_count": self.detection_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
