from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class CertificationLevel(str, enum.Enum):
    BEGINNER = "beginner"
    ASSOCIATE = "associate"
    PROFESSIONAL = "professional"
    SPECIALTY = "specialty"


class ExamVersionStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(SAEnum(CertificationLevel), nullable=False)
    category = Column(String(100), nullable=False)
    estimated_hours = Column(Integer, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    provider = relationship("Provider", back_populates="certifications")
    exam_versions = relationship("ExamVersion", back_populates="certification", order_by="ExamVersion.effective_date.desc()")
    products = relationship("Product", back_populates="certification")


class ExamVersion(Base):
    __tablename__ = "exam_versions"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    version = Column(String(50), nullable=False)
    effective_date = Column(DateTime, nullable=True)
    retirement_date = Column(DateTime, nullable=True)
    status = Column(SAEnum(ExamVersionStatus), default=ExamVersionStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    certification = relationship("Certification", back_populates="exam_versions")
    domains = relationship("Domain", back_populates="exam_version", order_by="Domain.order_index")
    questions = relationship("Question", back_populates="exam_version")
