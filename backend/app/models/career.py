from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class CareerPath(Base):
    __tablename__ = "career_paths"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    estimated_months = Column(Integer, nullable=True)
    skills_covered = Column(Text, nullable=True)  # JSON array of skills
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    certifications = relationship("CareerCertification", back_populates="career_path", cascade="all, delete-orphan")


class CareerCertification(Base):
    __tablename__ = "career_certifications"

    id = Column(Integer, primary_key=True, index=True)
    career_path_id = Column(Integer, ForeignKey("career_paths.id"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    stage = Column(String(100), nullable=False)  # foundation, intermediate, advanced, specialty
    order_index = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    required = Column(Boolean, default=False)

    career_path = relationship("CareerPath", back_populates="certifications")
    certification = relationship("Certification")


class UserCareerGoal(Base):
    __tablename__ = "user_career_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    career_path_id = Column(Integer, ForeignKey("career_paths.id"), nullable=True)
    goal_type = Column(String(100), nullable=True)  # get_first_job, switch_career, get_certified, etc.
    current_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    preferred_technology = Column(String(100), nullable=True)
    target_role = Column(String(255), nullable=True)
    daily_hours = Column(Integer, nullable=True)
    target_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    career_path = relationship("CareerPath")
