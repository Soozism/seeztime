"""
Bug Report model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import BugSeverity, BugStatus

class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text)
    severity = Column(Enum(BugSeverity), default=BugSeverity.MEDIUM)
    status = Column(Enum(BugStatus), default=BugStatus.OPEN)
    
    # Foreign keys
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    reported_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    task = relationship("Task", back_populates="bug_reports")
    reported_by = relationship("User", back_populates="bug_reports")

    def __repr__(self):
        return f"<BugReport {self.title}>"

# Add indexes for better performance
Index("idx_bugreport_task_id", BugReport.task_id)
Index("idx_bugreport_reported_by_id", BugReport.reported_by_id)
Index("idx_bugreport_status", BugReport.status)
Index("idx_bugreport_severity", BugReport.severity)
