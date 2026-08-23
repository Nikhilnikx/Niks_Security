from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from app.database import Base


class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False, default="threshold")  # threshold, pattern, anomaly, correlation
    severity = Column(String(20), default="medium", nullable=False)
    mitre_technique = Column(String(20), nullable=True)
    mitre_tactic = Column(String(100), nullable=True)
    conditions = Column(Text, nullable=True)  # JSON rule conditions
    enabled = Column(Boolean, default=True, nullable=False)
    false_positive_count = Column(Integer, default=0, nullable=False)
    true_positive_count = Column(Integer, default=0, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="detection_rules")
    alerts = relationship("Alert", back_populates="detection_rule")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rule_type": self.rule_type,
            "severity": self.severity,
            "mitre_technique": self.mitre_technique,
            "mitre_tactic": self.mitre_tactic,
            "conditions": self.conditions,
            "enabled": self.enabled,
            "false_positive_count": self.false_positive_count,
            "true_positive_count": self.true_positive_count,
            "last_triggered_at": self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
