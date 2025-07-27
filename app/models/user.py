"""
User model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

from app.core.database import Base
from app.models.enums import UserRole

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (using lazy loading to avoid circular imports)
    created_projects = relationship("Project", back_populates="created_by", lazy="dynamic")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id", lazy="dynamic")
    created_tasks = relationship("Task", back_populates="created_by", foreign_keys="Task.created_by_id", lazy="dynamic")
    time_logs = relationship("TimeLog", back_populates="user", lazy="dynamic")
    active_timers = relationship("ActiveTimer", back_populates="user", lazy="dynamic")
    bug_reports = relationship("BugReport", back_populates="reported_by", lazy="dynamic")
    
    # Team relationships
    led_teams = relationship("Team", back_populates="team_leader", lazy="dynamic")
    teams = relationship("Team", secondary="team_members", back_populates="members", lazy="dynamic")

    def set_password(self, password: str):
        """Set password hash"""
        self.password_hash = pwd_context.hash(password)

    def check_password(self, password: str) -> bool:
        """Check password against hash"""
        return pwd_context.verify(password, self.password_hash)

    @property
    def full_name(self) -> str:
        """Get full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username

    def __repr__(self):
        return f"<User {self.username}>"
