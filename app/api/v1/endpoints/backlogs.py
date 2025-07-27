"""
Backlog management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.backlog import Backlog
from app.models.project import Project
from app.models.task import Task
from app.schemas.backlog import BacklogCreate, BacklogUpdate, BacklogResponse

router = APIRouter()

@router.get("/", response_model=List[BacklogResponse])
def get_backlogs(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all backlogs with optional project filter"""
    query = db.query(Backlog)
    
    if project_id:
        query = query.filter(Backlog.project_id == project_id)
    
    backlogs = query.offset(skip).limit(limit).all()
    return backlogs

@router.get("/{backlog_id}", response_model=BacklogResponse)
def get_backlog(
    backlog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get backlog by ID"""
    backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")
    return backlog

@router.post("/", response_model=BacklogResponse)
def create_backlog(
    backlog: BacklogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new backlog item"""
    # Verify project exists
    project = db.query(Project).filter(Project.id == backlog.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_backlog = Backlog(**backlog.dict())
    db.add(db_backlog)
    db.commit()
    db.refresh(db_backlog)
    return db_backlog

@router.put("/{backlog_id}", response_model=BacklogResponse)
def update_backlog(
    backlog_id: int,
    backlog_update: BacklogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update backlog item"""
    backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")
    
    update_data = backlog_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(backlog, field, value)
    
    db.commit()
    db.refresh(backlog)
    return backlog

@router.delete("/{backlog_id}")
def delete_backlog(
    backlog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete backlog item"""
    backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")
    
    db.delete(backlog)
    db.commit()
    return {"message": "Backlog deleted successfully"}

@router.post("/{backlog_id}/convert-to-task")
def convert_backlog_to_task(
    backlog_id: int,
    sprint_id: int = None,
    assignee_id: int = None,
    estimated_hours: float = None,
    story_points: int = None,
    priority: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Convert backlog item to task with additional parameters"""
    backlog = db.query(Backlog).filter(Backlog.id == backlog_id).first()
    if not backlog:
        raise HTTPException(status_code=404, detail="Backlog not found")
    
    # Check permissions - only managers can convert backlogs
    if current_user.role.value not in ['admin', 'project_manager']:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Create task from backlog with enhanced fields
    from app.models.enums import TaskPriority
    task_priority = TaskPriority.MEDIUM
    if priority:
        try:
            task_priority = TaskPriority[priority.upper()]
        except KeyError:
            pass
    
    task = Task(
        title=backlog.title,
        description=backlog.description,
        project_id=backlog.project_id,
        sprint_id=sprint_id,
        assignee_id=assignee_id,
        estimated_hours=estimated_hours or 0.0,
        story_points=story_points or 0,
        priority=task_priority,
        created_by_id=current_user.id
    )
    db.add(task)
    
    # Delete backlog item
    db.delete(backlog)
    db.commit()
    db.refresh(task)
    
    return {
        "message": "Backlog converted to task successfully", 
        "task_id": task.id,
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "project_id": task.project_id,
            "sprint_id": task.sprint_id,
            "assignee_id": task.assignee_id,
            "estimated_hours": task.estimated_hours,
            "story_points": task.story_points,
            "priority": task.priority.value
        }
    }
