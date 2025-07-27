"""
Active Timer model for live time tracking
"""

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class ActiveTimer(Base):
    __tablename__ = "active_timers"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="active_timers")
    user = relationship("User", back_populates="active_timers")

    def __repr__(self):
        return f"<ActiveTimer {self.id} for {self.task.title} by {self.user.username}>"


# Add indexes for better performance
Index("idx_active_timer_task_id", ActiveTimer.task_id)
Index("idx_active_timer_user_id", ActiveTimer.user_id)
Index("idx_active_timer_is_active", ActiveTimer.is_active)
