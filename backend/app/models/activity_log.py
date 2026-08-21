from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # quiz, mock_exam, study, flashcard
    duration_minutes = Column(Float, default=0)
    activity_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity_logs")
