from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), default=UserRole.USER, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    answers = relationship("UserAnswer", back_populates="user")
    quizzes = relationship("Quiz", back_populates="user")
    mock_exams = relationship("MockExam", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    mastery_scores = relationship("MasteryScore", back_populates="user")
    purchases = relationship("Purchase", back_populates="user")
    entitlements = relationship("UserEntitlement", back_populates="user")
    documents = relationship("Document", back_populates="user")
    study_plans = relationship("StudyPlan", back_populates="user")
    flashcards = relationship("UserFlashcard", back_populates="user")
    ai_conversations = relationship("AIConversation", back_populates="user")
    concept_progress = relationship("ConceptProgress", back_populates="user")
    bookmarks = relationship("Bookmark", back_populates="user")
    notes = relationship("UserNote", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
