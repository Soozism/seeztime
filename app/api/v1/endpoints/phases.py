"""
Phase API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models import Phase, Project, User
from app.schemas.phase import PhaseCreate, PhaseUpdate, PhaseResponse

router = APIRouter()

@router.post("/", response_model=PhaseResponse)
def create_phase(
    phase_create: PhaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new phase"""
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == phase_create.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create phase
    phase = Phase(
        name=phase_create.name,
        description=phase_create.description,
        estimated_hours=phase_create.estimated_hours,
        start_date=phase_create.start_date,
        end_date=phase_create.end_date,
        project_id=phase_create.project_id
    )
    
    db.add(phase)
    db.commit()
    db.refresh(phase)
    
    return PhaseResponse.from_orm_with_expansions(phase, include_project_name=True)

@router.get("/", response_model=List[PhaseResponse])
def list_phases(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    include_project_name: bool = Query(False, description="Include project name in response"),
    skip: int = Query(0, ge=0, description="Number of phases to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of phases to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List phases with optional filtering"""
    query = db.query(Phase)
    
    if project_id:
        query = query.filter(Phase.project_id == project_id)
    
    if include_project_name:
        query = query.options(joinedload(Phase.project))
    
    query = query.options(joinedload(Phase.milestones))
    phases = query.offset(skip).limit(limit).all()
    
    return [PhaseResponse.from_orm_with_expansions(phase, include_project_name=include_project_name) for phase in phases]

@router.get("/{phase_id}", response_model=PhaseResponse)
def get_phase(
    phase_id: int,
    include_project_name: bool = Query(False, description="Include project name in response"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific phase by ID"""
    query = db.query(Phase).options(joinedload(Phase.milestones))
    
    if include_project_name:
        query = query.options(joinedload(Phase.project))
    
    phase = query.filter(Phase.id == phase_id).first()
    
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    return PhaseResponse.from_orm_with_expansions(phase, include_project_name=include_project_name)

@router.put("/{phase_id}", response_model=PhaseResponse)
def update_phase(
    phase_id: int,
    phase_update: PhaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a phase"""
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    # Update fields
    update_data = phase_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(phase, field, value)
    
    db.commit()
    db.refresh(phase)
    
    return PhaseResponse.from_orm_with_expansions(phase, include_project_name=True)

@router.delete("/{phase_id}")
def delete_phase(
    phase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a phase"""
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    # Check if phase has milestones
    if phase.milestones:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete phase with existing milestones. Please delete milestones first."
        )
    
    db.delete(phase)
    db.commit()
    
    return {"message": "Phase deleted successfully"}

@router.get("/{phase_id}/milestones")
def get_phase_milestones(
    phase_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all milestones for a specific phase"""
    phase = db.query(Phase).filter(Phase.id == phase_id).first()
    
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")
    
    from app.schemas.milestone import MilestoneResponse
    
    milestones = db.query(Phase).options(
        joinedload(Phase.milestones)
    ).filter(Phase.id == phase_id).first().milestones
    
    return [MilestoneResponse.from_orm_with_expansions(milestone, include_names=True) for milestone in milestones]
