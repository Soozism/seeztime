"""
Completed Story Points model
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class CompletedStoryPoints(Base):
    __tablename__ = "completed_story_points"

    id = Column(Integer, primary_key=True, index=True)
    story_points = Column(Integer, nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sprint = relationship("Sprint")
    user = relationship("User")

    def __repr__(self):
        return f"<CompletedStoryPoints {self.story_points} by {self.user.username}>"
