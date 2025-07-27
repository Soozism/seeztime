"""
Task Statistics model for reporting and analytics
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class TaskStatistics(Base):
    __tablename__ = "task_statistics"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    completed_tasks = Column(Integer, default=0)
    avg_completion_time = Column(Float, default=0.0)
    total_story_points = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project")
    sprint = relationship("Sprint")

    def __repr__(self):
        return f"<TaskStatistics project_id={self.project_id}>"


# Add indexes for better performance
Index("idx_task_statistics_project_id", TaskStatistics.project_id)
Index("idx_task_statistics_sprint_id", TaskStatistics.sprint_id)
