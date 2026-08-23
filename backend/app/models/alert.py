import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, enum.Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(SAEnum(AlertSeverity), default=AlertSeverity.LOW, nullable=False, index=True)
    status = Column(SAEnum(AlertStatus), default=AlertStatus.NEW, nullable=False, index=True)
    risk_score = Column(Float, default=0.0, nullable=False)
    confidence = Column(Float, default=0.0, nullable=False)
    source_ip = Column(String(45), nullable=True, index=True)
    destination_ip = Column(String(45), nullable=True)
    username = Column(String(120), nullable=True)
    hostname = Column(String(255), nullable=True)
    mitre_technique = Column(String(20), nullable=True)
    mitre_tactic = Column(String(100), nullable=True)
    evidence = Column(Text, nullable=True)
    recommended_actions = Column(Text, nullable=True)
    analyst_notes = Column(Text, nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("security_events.id"), nullable=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    detection_rule_id = Column(Integer, ForeignKey("detection_rules.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="alerts")
    event = relationship("SecurityEvent", back_populates="alert")
    asset = relationship("Asset", back_populates="alerts")
    assignee = relationship("User", back_populates="alerts")
    detection_rule = relationship("DetectionRule", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value if self.severity else "low",
            "status": self.status.value if self.status else "new",
            "risk_score": self.risk_score,
            "confidence": self.confidence,
            "source_ip": self.source_ip,
            "destination_ip": self.destination_ip,
            "username": self.username,
            "hostname": self.hostname,
            "mitre_technique": self.mitre_technique,
            "mitre_tactic": self.mitre_tactic,
            "evidence": self.evidence,
            "recommended_actions": self.recommended_actions,
            "analyst_notes": self.analyst_notes,
            "assignee_id": self.assignee_id,
            "event_id": self.event_id,
            "asset_id": self.asset_id,
            "detection_rule_id": self.detection_rule_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
