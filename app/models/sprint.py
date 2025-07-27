"""
Sprint model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import SprintStatus

class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(SprintStatus), default=SprintStatus.PLANNED)
    estimated_hours = Column(Float, CheckConstraint("estimated_hours >= 0"), default=0.0)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)  # Keep for backward compatibility
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    milestone = relationship("Milestone", back_populates="sprints")
    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")

    def __repr__(self):
        return f"<Sprint {self.name}>"
