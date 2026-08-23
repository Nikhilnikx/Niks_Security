from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    report_type = Column(String(50), nullable=False)  # security_summary, incident, threat, executive, detection
    content = Column(Text, nullable=True)  # JSON report data
    format = Column(String(10), default="json", nullable=False)  # json, csv, pdf
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="reports")
