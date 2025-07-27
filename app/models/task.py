"""
Task model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float, Boolean, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import TaskStatus, TaskPriority

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    story_points = Column(Integer, CheckConstraint("story_points >= 0"), default=0)
    estimated_hours = Column(Float, CheckConstraint("estimated_hours >= 0"), default=0.0)
    actual_hours = Column(Float, CheckConstraint("actual_hours >= 0"), default=0.0)
    is_subtask = Column(Boolean, default=False)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True))

    # Relationships
    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    created_by = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    parent_task = relationship("Task", remote_side=[id], back_populates="subtasks")
    subtasks = relationship("Task", back_populates="parent_task", cascade="all, delete-orphan")
    time_logs = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan")
    active_timers = relationship("ActiveTimer", back_populates="task", cascade="all, delete-orphan")
    bug_reports = relationship("BugReport", back_populates="task", cascade="all, delete-orphan")
    # tags relationship will be configured after all models are loaded

    def __repr__(self):
        return f"<Task {self.title}>"


# Configure the tags relationship after all models are defined
def configure_task_tags_relationship():
    """Configure the many-to-many relationship between tasks and tags"""
    from app.models.tag import task_tags
    Task.tags = relationship("Tag", secondary=task_tags, back_populates="tasks")


# Add indexes for better performance
Index("idx_task_project_id", Task.project_id)
Index("idx_task_sprint_id", Task.sprint_id)
Index("idx_task_assignee_id", Task.assignee_id)
Index("idx_task_status", Task.status)
Index("idx_task_priority", Task.priority)
Index("idx_task_parent_task_id", Task.parent_task_id)
