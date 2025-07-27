"""
Milestone model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    estimated_hours = Column(Float, CheckConstraint("estimated_hours >= 0"), default=0.0)
    phase_id = Column(Integer, ForeignKey("phases.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)  # Keep for backward compatibility
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    phase = relationship("Phase", back_populates="milestones")
    project = relationship("Project", back_populates="milestones")
    sprints = relationship("Sprint", back_populates="milestone", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Milestone {self.name}>"
