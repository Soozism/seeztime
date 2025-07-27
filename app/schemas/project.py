"""
Project schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.enums import ProjectStatus

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_hours: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.ACTIVE

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[ProjectStatus] = None

# Simple project info for embedding in other responses
class ProjectSimple(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    estimated_hours: float = 0.0
    status: ProjectStatus
    
    class Config:
        from_attributes = True

class ProjectResponse(ProjectBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Task counts
    total_tasks: int = 0
    done_tasks: int = 0

    # Time tracking
    total_spent_hours: float = 0.0

    # Completion percentage
    completion_percentage: float = 0.0

    # Optional expanded fields
    created_by_username: Optional[str] = None
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_expansions(cls, project, total_tasks=0, done_tasks=0, total_spent_hours=0.0, completion_percentage=0.0):
        """Create response with expanded relationship data, task counts, time tracking, and completion percentage"""
        data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "status": project.status,
            "created_by_id": project.created_by_id,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "total_tasks": total_tasks,
            "done_tasks": done_tasks,
            "total_spent_hours": total_spent_hours,
            "completion_percentage": completion_percentage,
        }

        # Add expanded data if relationships are loaded
        if hasattr(project, 'created_by') and project.created_by:
            data["created_by_username"] = project.created_by.username
            if project.created_by.first_name and project.created_by.last_name:
                data["created_by_name"] = f"{project.created_by.first_name} {project.created_by.last_name}"
            elif project.created_by.first_name:
                data["created_by_name"] = project.created_by.first_name

        return cls(**data)


# Enhanced project response with detailed statistics
class TaskSummary(BaseModel):
    total: int = 0
    todo: int = 0
    in_progress: int = 0
    review: int = 0
    done: int = 0
    todo_percentage: float = 0.0
    in_progress_percentage: float = 0.0
    review_percentage: float = 0.0
    done_percentage: float = 0.0

class SprintSummary(BaseModel):
    total: int = 0
    planned: int = 0
    active: int = 0
    completed: int = 0
    planned_percentage: float = 0.0
    active_percentage: float = 0.0
    completed_percentage: float = 0.0
    total_estimated_hours: float = 0.0
    planned_estimated_hours: float = 0.0
    active_estimated_hours: float = 0.0
    completed_estimated_hours: float = 0.0

class MilestoneSummary(BaseModel):
    total: int = 0
    pending: int = 0
    completed: int = 0
    pending_percentage: float = 0.0
    completed_percentage: float = 0.0
    total_estimated_hours: float = 0.0
    pending_estimated_hours: float = 0.0
    completed_estimated_hours: float = 0.0

class PhaseSummary(BaseModel):
    total: int = 0
    total_estimated_hours: float = 0.0

class UserProjectStats(BaseModel):
    user_id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    total_hours: float = 0.0
    total_story_points: int = 0
    tasks_completed: int = 0
    tasks_in_progress: int = 0
    tasks_total: int = 0

class ProjectUsersSummary(BaseModel):
    total_project_hours: float = 0.0
    total_project_story_points: int = 0
    active_users_count: int = 0
    users_stats: List[UserProjectStats] = []

class ProjectDetailedResponse(ProjectBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Optional expanded fields
    created_by_username: Optional[str] = None
    created_by_name: Optional[str] = None

    # Detailed statistics
    task_summary: TaskSummary
    sprint_summary: SprintSummary
    milestone_summary: MilestoneSummary
    phase_summary: PhaseSummary
    users_summary: Optional[ProjectUsersSummary] = None

    # Completion percentage
    completion_percentage: float = 0.0

    # Detailed lists (optional based on include_details parameter)
    tasks: Optional[List[Dict[str, Any]]] = None
    sprints: Optional[List[Dict[str, Any]]] = None
    milestones: Optional[List[Dict[str, Any]]] = None
    phases: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True
