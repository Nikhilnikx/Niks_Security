from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    exam_version_id = Column(Integer, ForeignKey("exam_versions.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    weight_percentage = Column(Float, nullable=False)
    order_index = Column(Integer, nullable=False)

    exam_version = relationship("ExamVersion", back_populates="domains")
    topics = relationship("Topic", back_populates="domain", order_by="Topic.order_index")
    questions = relationship("Question", back_populates="domain")
