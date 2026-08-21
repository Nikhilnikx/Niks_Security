from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ReportReason(str, enum.Enum):
    INCORRECT_ANSWER = "incorrect_answer"
    INCORRECT_EXPLANATION = "incorrect_explanation"
    TYPO = "typo"
    AMBIGUOUS = "ambiguous"
    DUPLICATE = "duplicate"
    OUTDATED = "outdated"
    OTHER = "other"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class QuestionReport(Base):
    __tablename__ = "question_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    reason = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User")
    question = relationship("Question")
