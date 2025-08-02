"""
Models package initialization
"""

# Import all models and association tables to ensure proper SQLAlchemy configuration
from .user import User
from .enums import UserRole, TaskStatus, TaskPriority, ProjectStatus, SprintStatus, BugSeverity, BugStatus
from .tag import Tag, task_tags  # Import association table first
from .project import Project
from .phase import Phase
from .team import Team, team_members, team_projects
from .sprint import Sprint
from .milestone import Milestone
from .task import Task, configure_task_tags_relationship
from .planner_event import PlannerEvent, PersonalTodo
from .task_dependency import TaskDependency
from .backlog import Backlog
from .bug_report import BugReport
from .time_log import TimeLog
from .active_timer import ActiveTimer
from .completed_sp import CompletedStoryPoints
from .version import Version
from .task_statistics import TaskStatistics
from .translation import Translation
from .working_hours import WorkingHours, Holiday, TimeOff

# Configure relationships that depend on multiple models
configure_task_tags_relationship()

__all__ = [
    "User", "UserRole", "TaskStatus", "TaskPriority", "ProjectStatus", "SprintStatus",
    "BugSeverity", "BugStatus", "Tag", "task_tags", "Project", "Phase", "Team", "team_members", 
    "team_projects", "Sprint", "Milestone", "Task", "TaskDependency", "Backlog", 
    "BugReport", "TimeLog", "ActiveTimer", "CompletedStoryPoints", "Version", "TaskStatistics", "Translation",
    "PlannerEvent", "PersonalTodo", "WorkingHours", "Holiday", "TimeOff"
]