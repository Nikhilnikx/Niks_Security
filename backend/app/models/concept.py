from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum as SAEnum, DateTime
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ConceptDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), index=True, nullable=False)
    short_definition = Column(Text, nullable=True)
    simple_explanation = Column(Text, nullable=True)
    detailed_explanation = Column(Text, nullable=True)
    examples = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)
    exam_tips = Column(Text, nullable=True)
    common_mistakes = Column(Text, nullable=True)
    difficulty = Column(SAEnum(ConceptDifficulty), default=ConceptDifficulty.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    topic = relationship("Topic", back_populates="concepts")
    questions = relationship("Question", back_populates="concept")
    learning_resources = relationship("LearningResource", back_populates="concept")
    flashcards = relationship("Flashcard", back_populates="concept")
    source_relationships = relationship(
        "ConceptRelationship",
        foreign_keys="ConceptRelationship.source_concept_id",
        back_populates="source_concept"
    )
    target_relationships = relationship(
        "ConceptRelationship",
        foreign_keys="ConceptRelationship.target_concept_id",
        back_populates="target_concept"
    )
