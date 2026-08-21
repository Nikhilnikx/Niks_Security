from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ResourceType(str, enum.Enum):
    OFFICIAL_DOCUMENTATION = "official_documentation"
    OFFICIAL_TRAINING = "official_training"
    ARTICLE = "article"
    VIDEO = "video"
    LESSON = "lesson"
    UPLOADED_DOCUMENT = "uploaded_document"


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    source = Column(String(255), nullable=True)
    resource_type = Column(SAEnum(ResourceType), nullable=False)
    is_official = Column(Boolean, default=False)

    concept = relationship("Concept", back_populates="learning_resources")
