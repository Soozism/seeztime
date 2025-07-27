"""
Time Log model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    hours = Column(Float, CheckConstraint("hours >= 0"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")

    def __repr__(self):
        return f"<TimeLog {self.hours}h for {self.task.title}>"


# Add indexes for better performance
Index("idx_timelog_task_id", TimeLog.task_id)
Index("idx_timelog_user_id", TimeLog.user_id)
Index("idx_timelog_date", TimeLog.date)
