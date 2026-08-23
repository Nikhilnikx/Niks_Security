import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base


class IncidentSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IncidentStatus(str, enum.Enum):
    NEW = "new"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(SAEnum(IncidentSeverity), default=IncidentSeverity.LOW, nullable=False)
    status = Column(SAEnum(IncidentStatus), default=IncidentStatus.NEW, nullable=False, index=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution = Column(Text, nullable=True)
    timeline = Column(Text, nullable=True)  # JSON array of timeline events
    iocs = Column(Text, nullable=True)  # JSON array of IOCs
    evidence = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)

    # Relationships
    organization = relationship("Organization", back_populates="incidents")
    alert_links = relationship("IncidentAlert", back_populates="incident")


class IncidentAlert(Base):
    __tablename__ = "incident_alerts"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    linked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    incident = relationship("Incident", back_populates="alert_links")
    alert = relationship("Alert")
