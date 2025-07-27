"""
Tag model
"""

from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

# Association table for many-to-many relationship between tasks and tags
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#007bff")  # Hex color code
    description = Column(Text)
    category = Column(String(50))

    # Relationships
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.name}>"
