from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)  # auth, network, firewall, app, system, web
    description = Column(Text, nullable=True)
    source_ip = Column(String(45), nullable=True, index=True)
    destination_ip = Column(String(45), nullable=True)
    source_port = Column(Integer, nullable=True)
    destination_port = Column(Integer, nullable=True)
    username = Column(String(120), nullable=True)
    hostname = Column(String(255), nullable=True)
    protocol = Column(String(20), nullable=True)
    action = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    severity = Column(String(20), default="low", nullable=False, index=True)
    risk_score = Column(Float, default=0.0, nullable=False)
    raw_log = Column(Text, nullable=True)
    parsed_data = Column(Text, nullable=True)  # JSON string for extra fields
    is_flagged = Column(Boolean, default=False, nullable=False)
    source_file = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="security_events")
    user = relationship("User", back_populates="security_events")
    asset = relationship("Asset", back_populates="security_events")
    alert = relationship("Alert", back_populates="event", uselist=False)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "category": self.category,
            "description": self.description,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "source_port": self.source_port,
            "destination_port": self.destination_port,
            "username": self.username,
            "hostname": self.hostname,
            "protocol": self.protocol,
            "action": self.action,
            "status": self.status,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "raw_log": self.raw_log,
            "is_flagged": self.is_flagged,
            "source_file": self.source_file,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
