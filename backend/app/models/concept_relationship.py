from sqlalchemy import Column, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class RelationshipType(str, enum.Enum):
    IS_A = "is_a"
    RELATED_TO = "related_to"
    COMPARED_WITH = "compared_with"
    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"


class ConceptRelationship(Base):
    __tablename__ = "concept_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    target_concept_id = Column(Integer, ForeignKey("concepts.id"), nullable=False)
    relationship_type = Column(SAEnum(RelationshipType), nullable=False)

    source_concept = relationship("Concept", foreign_keys=[source_concept_id], back_populates="source_relationships")
    target_concept = relationship("Concept", foreign_keys=[target_concept_id], back_populates="target_relationships")
