from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    total_questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    concepts_completed = Column(Integer, default=0)
    total_concepts = Column(Integer, default=0)
    last_activity = Column(DateTime, default=datetime.utcnow)
    streak_days = Column(Integer, default=0)
    last_streak_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="progress")


class ConceptProgress(Base):
    __tablename__ = "concept_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    completed = Column(Boolean, default=False)
    mastery_level = Column(Float, default=0.0)  # 0-100
    last_studied = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="concept_progress")


class MasteryScore(Base):
    __tablename__ = "mastery_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    score = Column(Float, default=0.0)  # 0-100
    questions_attempted = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="mastery_scores")
