"""
Phase model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    estimated_hours = Column(Float, CheckConstraint("estimated_hours >= 0"), default=0.0)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="phases")
    milestones = relationship("Milestone", back_populates="phase", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Phase {self.name}>"
