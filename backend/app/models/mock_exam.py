from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class MockExamStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class MockExam(Base):
    __tablename__ = "mock_exams"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    total_questions = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    score = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)  # seconds
    status = Column(SAEnum(MockExamStatus), default=MockExamStatus.IN_PROGRESS)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="mock_exams")
    questions = relationship("MockExamQuestion", back_populates="mock_exam", cascade="all, delete-orphan")


class MockExamQuestion(Base):
    __tablename__ = "mock_exam_questions"

    id = Column(Integer, primary_key=True, index=True)
    mock_exam_id = Column(Integer, ForeignKey("mock_exams.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("question_options.id"), nullable=True)
    is_correct = Column(Integer, nullable=True)
    flagged = Column(Integer, default=0)
    order_index = Column(Integer, nullable=False)

    mock_exam = relationship("MockExam", back_populates="questions")
    question = relationship("Question", back_populates="mock_exam_questions")


class MockExamConfig(Base):
    __tablename__ = "mock_exam_configs"

    id = Column(Integer, primary_key=True, index=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=False)
    number_of_questions = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    passing_score = Column(Integer, default=70)
    description = Column(Text, nullable=True)
