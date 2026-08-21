from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    version = Column(String(50), nullable=False)
    content_status = Column(String(50), default="current")  # current, review_needed, outdated, archived
    last_reviewed = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    next_review = Column(DateTime, nullable=True)
    changes_summary = Column(Text, nullable=True)

    certification = relationship("Certification")


class ContentUpdateLog(Base):
    __tablename__ = "content_update_logs"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    update_type = Column(String(50), nullable=False)  # new_content, updated_content, new_question, new_resource
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    affected_domains = Column(Text, nullable=True)
    affected_topics = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
