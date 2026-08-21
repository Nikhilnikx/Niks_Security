from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(Integer, ForeignKey("question_options.id"), nullable=True)
    is_correct = Column(Boolean, nullable=False)
    response_time = Column(Float, nullable=True)  # seconds
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="user_answers")
    selected_option = relationship("QuestionOption")
