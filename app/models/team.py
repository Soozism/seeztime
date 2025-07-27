"""
Team model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

# Association table for team members (many-to-many relationship)
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', String(50)),
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)

# Association table for team-project assignments (many-to-many relationship)
team_projects = Table(
    'team_projects',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
    Column('role', String(50)),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    team_leader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    team_leader = relationship("User", foreign_keys=[team_leader_id], back_populates="led_teams")
    members = relationship("User", secondary=team_members, back_populates="teams")
    projects = relationship("Project", secondary=team_projects, back_populates="teams")
