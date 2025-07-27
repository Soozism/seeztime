"""
Milestone schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MilestoneBase(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_hours: float = 0.0
    due_date: Optional[datetime] = None

class MilestoneCreate(MilestoneBase):
    phase_id: int
    project_id: Optional[int] = None  # Keep for backward compatibility

class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class MilestoneResponse(MilestoneBase):
    id: int
    phase_id: int
    project_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    phase_name: Optional[str] = None
    project_name: Optional[str] = None
    sprint_count: int = 0
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_expansions(cls, milestone, include_names: bool = False):
        """Create response with optional expanded fields"""
        data = {
            "id": milestone.id,
            "name": milestone.name,
            "description": milestone.description,
            "estimated_hours": milestone.estimated_hours,
            "due_date": milestone.due_date,
            "phase_id": milestone.phase_id,
            "project_id": milestone.project_id,
            "completed_at": milestone.completed_at,
            "created_at": milestone.created_at,
            "updated_at": milestone.updated_at,
            "sprint_count": len(milestone.sprints) if hasattr(milestone, 'sprints') else 0,
        }
        
        if include_names:
            if hasattr(milestone, 'phase') and milestone.phase:
                data["phase_name"] = milestone.phase.name
            if hasattr(milestone, 'project') and milestone.project:
                data["project_name"] = milestone.project.name
                
        return cls(**data)
