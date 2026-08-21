from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class QuestionType(str, enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SCENARIO = "scenario"


class AccessLevel(str, enum.Enum):
    FREE = "FREE"
    PREMIUM = "PREMIUM"


class QuestionDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_version_id = Column(Integer, ForeignKey("exam_versions.id"), nullable=False)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(SAEnum(QuestionType), default=QuestionType.SINGLE_CHOICE, nullable=False)
    difficulty = Column(SAEnum(QuestionDifficulty), default=QuestionDifficulty.MEDIUM)
    access_level = Column(SAEnum(AccessLevel), default=AccessLevel.FREE, nullable=False)
    explanation = Column(Text, nullable=True)
    source_type = Column(String(100), nullable=True)  # e.g., "original", "practice", "exam-style"
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    # Quality metrics
    attempt_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_response_time = Column(Float, default=0.0)
    quality_score = Column(Float, default=50.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    exam_version = relationship("ExamVersion", back_populates="questions")
    domain = relationship("Domain", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    concept = relationship("Concept", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="question")
    quiz_questions = relationship("QuizQuestion", back_populates="question")
    mock_exam_questions = relationship("MockExamQuestion", back_populates="question")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)

    question = relationship("Question", back_populates="options")
