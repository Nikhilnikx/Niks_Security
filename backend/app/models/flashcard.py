from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    concept = relationship("Concept", back_populates="flashcards")
    user_flashcards = relationship("UserFlashcard", back_populates="flashcard")


class UserFlashcard(Base):
    __tablename__ = "user_flashcards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    is_user_created = Column(Integer, default=0)  # 0 = system, 1 = user
    last_reviewed = Column(DateTime, nullable=True)
    confidence = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    next_review = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="flashcards")
    flashcard = relationship("Flashcard", back_populates="user_flashcards")
