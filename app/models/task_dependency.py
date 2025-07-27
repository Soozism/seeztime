"""
Task Dependency model
"""

from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.core.database import Base

class TaskDependency(Base):
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    depends_on_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    # Relationships
    task = relationship("Task", foreign_keys=[task_id], backref="dependencies")
    depends_on_task = relationship("Task", foreign_keys=[depends_on_task_id], backref="dependent_tasks")

    def __repr__(self):
        return f"<TaskDependency {self.task_id} -> {self.depends_on_task_id}>"


# Add indexes for better performance
Index("idx_task_dependency_task_id", TaskDependency.task_id)
Index("idx_task_dependency_depends_on_task_id", TaskDependency.depends_on_task_id)
