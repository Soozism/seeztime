"""
Sprint schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import SprintStatus

class SprintBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: SprintStatus = SprintStatus.PLANNED
    estimated_hours: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class SprintCreate(SprintBase):
    milestone_id: int
    project_id: Optional[int] = None  # Keep for backward compatibility

class SprintUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[SprintStatus] = None
    estimated_hours: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Simple sprint info for embedding in other responses
class SprintSimple(BaseModel):
    id: int
    name: str
    status: SprintStatus
    estimated_hours: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SprintResponse(SprintBase):
    id: int
    milestone_id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    milestone_name: Optional[str] = None
    project_name: Optional[str] = None
    task_count: int = 0
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_expansions(cls, sprint, include_names: bool = False):
        """Create response with optional expanded fields"""
        data = {
            "id": sprint.id,
            "name": sprint.name,
            "description": sprint.description,
            "status": sprint.status,
            "estimated_hours": sprint.estimated_hours,
            "start_date": sprint.start_date,
            "end_date": sprint.end_date,
            "milestone_id": sprint.milestone_id,
            "project_id": sprint.project_id,
            "created_at": sprint.created_at,
            "updated_at": sprint.updated_at,
            "task_count": len(sprint.tasks) if hasattr(sprint, 'tasks') else 0,
        }
        
        if include_names:
            if hasattr(sprint, 'milestone') and sprint.milestone:
                data["milestone_name"] = sprint.milestone.name
            if hasattr(sprint, 'project') and sprint.project:
                data["project_name"] = sprint.project.name
                
        return cls(**data)
