"""
Phase schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PhaseBase(BaseModel):
    name: str
    description: Optional[str] = None
    estimated_hours: float = 0.0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PhaseCreate(PhaseBase):
    project_id: int

class PhaseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    estimated_hours: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class PhaseSimple(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    estimated_hours: float
    
    class Config:
        from_attributes = True

class PhaseResponse(PhaseBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    project_name: Optional[str] = None
    milestone_count: int = 0
    total_milestones: int = 0
    completed_milestones: int = 0
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm_with_expansions(cls, phase, include_project_name: bool = False):
        """Create response with optional expanded fields"""
        data = {
            "id": phase.id,
            "name": phase.name,
            "description": phase.description,
            "estimated_hours": phase.estimated_hours,
            "start_date": phase.start_date,
            "end_date": phase.end_date,
            "project_id": phase.project_id,
            "created_at": phase.created_at,
            "updated_at": phase.updated_at,
            "milestone_count": len(phase.milestones) if hasattr(phase, 'milestones') else 0,
            "total_milestones": len(phase.milestones) if hasattr(phase, 'milestones') else 0,
        }
        
        if include_project_name and hasattr(phase, 'project') and phase.project:
            data["project_name"] = phase.project.name
            
        # Calculate completed milestones
        if hasattr(phase, 'milestones'):
            completed = sum(1 for m in phase.milestones if m.completed_at is not None)
            data["completed_milestones"] = completed
            
        return cls(**data)
