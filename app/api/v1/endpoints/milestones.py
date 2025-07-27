"""
Milestone management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.milestone import Milestone
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.team import Team
from app.models.enums import UserRole
from app.schemas.milestone import MilestoneCreate, MilestoneUpdate, MilestoneResponse

router = APIRouter()

def can_manage_milestones_in_project(user: User, project: Project, db: Session) -> bool:
    """Check if user can manage milestones in project"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    
    # Team leaders can manage milestones in their assigned projects
    if user.role == UserRole.TEAM_LEADER:
        return db.query(Team).filter(
            Team.team_leader_id == user.id,
            Team.projects.any(Project.id == project.id)
        ).first() is not None
    
    return False

@router.get("/", response_model=List[MilestoneResponse])
def get_milestones(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    phase_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all milestones with optional filters"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Milestone).options(
        joinedload(Milestone.phase),
        joinedload(Milestone.project)
    )
    
    if project_id:
        query = query.filter(Milestone.project_id == project_id)
    if phase_id:
        query = query.filter(Milestone.phase_id == phase_id)
    
    milestones = query.offset(skip).limit(limit).all()
    return [MilestoneResponse.from_orm_with_expansions(milestone, include_names=True) for milestone in milestones]

@router.get("/{milestone_id}", response_model=MilestoneResponse)
def get_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get milestone by ID"""
    from sqlalchemy.orm import joinedload
    
    milestone = db.query(Milestone).options(
        joinedload(Milestone.phase),
        joinedload(Milestone.project),
        joinedload(Milestone.sprints)
    ).filter(Milestone.id == milestone_id).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    return MilestoneResponse.from_orm_with_expansions(milestone, include_names=True)

@router.post("/", response_model=MilestoneResponse)
def create_milestone(
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new milestone"""
    from app.models.phase import Phase
    
    # Verify phase exists
    phase = db.query(Phase).filter(Phase.id == milestone_data.phase_id).first()
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    # Check permissions - only team leaders, project managers, and admins can create milestones
    project = db.query(Project).filter(Project.id == phase.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not can_manage_milestones_in_project(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    milestone = Milestone(
        name=milestone_data.name,
        description=milestone_data.description,
        estimated_hours=milestone_data.estimated_hours,
        due_date=milestone_data.due_date,
        phase_id=milestone_data.phase_id,
        project_id=phase.project_id  # Set for backward compatibility
    )
    
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    
    # Load relationships for response
    from sqlalchemy.orm import joinedload
    db.refresh(milestone)
    milestone = db.query(Milestone).options(
        joinedload(Milestone.phase),
        joinedload(Milestone.project)
    ).filter(Milestone.id == milestone.id).first()
    
    return MilestoneResponse.from_orm_with_expansions(milestone, include_names=True)

@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone(
    milestone_id: int,
    milestone_data: MilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Check permissions
    project = milestone.project
    if not can_manage_milestones_in_project(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update fields if provided
    if milestone_data.name is not None:
        milestone.name = milestone_data.name
    if milestone_data.description is not None:
        milestone.description = milestone_data.description
    if milestone_data.due_date is not None:
        milestone.due_date = milestone_data.due_date
    if milestone_data.sprint_id is not None:
        if milestone_data.sprint_id > 0:
            sprint = db.query(Sprint).filter(Sprint.id == milestone_data.sprint_id).first()
            if not sprint:
                raise HTTPException(status_code=404, detail="Sprint not found")
            if sprint.project_id != milestone.project_id:
                raise HTTPException(status_code=400, detail="Sprint does not belong to the same project")
        milestone.sprint_id = milestone_data.sprint_id if milestone_data.sprint_id > 0 else None
    
    db.commit()
    db.refresh(milestone)
    return milestone

@router.patch("/{milestone_id}/complete")
def complete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark milestone as completed"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Check permissions
    project = milestone.project
    if not can_manage_milestones_in_project(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    milestone.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(milestone)
    return milestone

@router.patch("/{milestone_id}/reopen")
def reopen_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reopen completed milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Check permissions
    project = milestone.project
    if not can_manage_milestones_in_project(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    milestone.completed_at = None
    db.commit()
    db.refresh(milestone)
    return milestone

@router.delete("/{milestone_id}")
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete milestone"""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    # Check permissions
    project = milestone.project
    if not can_manage_milestones_in_project(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(milestone)
    db.commit()
    return {"message": "Milestone deleted successfully"}
