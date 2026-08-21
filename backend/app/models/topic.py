from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)

    domain = relationship("Domain", back_populates="topics")
    concepts = relationship("Concept", back_populates="topic", order_by="Concept.id")
    questions = relationship("Question", back_populates="topic")
