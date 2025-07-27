"""
Sprint management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.sprint import Sprint
from app.models.project import Project
from app.models.team import Team
from app.models.task import Task
from app.models.enums import UserRole
from app.schemas.sprint import SprintCreate, SprintUpdate, SprintResponse
from app.schemas.task import TaskResponse

router = APIRouter()

# Bulk task operations schema
class BulkTasksRequest(BaseModel):
    task_ids: List[int]

def can_manage_sprints_in_project(user: User, project: Project, db: Session) -> bool:
    """Check if user can manage sprints in project"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    
    # Team leaders can manage sprints in their assigned projects
    if user.role == UserRole.TEAM_LEADER:
        return db.query(Team).filter(
            Team.team_leader_id == user.id,
            Team.projects.any(Project.id == project.id)
        ).first() is not None
    
    return False

@router.get("/", response_model=List[SprintResponse])
def get_sprints(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sprints with optional project filter"""
    query = db.query(Sprint)
    
    if project_id:
        query = query.filter(Sprint.project_id == project_id)
    
    # Role-based filtering
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Get teams the user is in
        if current_user.role == UserRole.TEAM_LEADER:
            # Team leaders see sprints from their teams' projects
            team_projects = db.query(Project).join(Team.projects).filter(
                Team.team_leader_id == current_user.id
            ).all()
        else:
            # Regular users see sprints from their teams' projects
            team_projects = db.query(Project).join(Team.projects).join(Team.members).filter(
                User.id == current_user.id
            ).all()
        
        project_ids = [p.id for p in team_projects]
        if project_ids:
            query = query.filter(Sprint.project_id.in_(project_ids))
        else:
            return []  # No access to any projects
    
    sprints = query.offset(skip).limit(limit).all()
    return sprints

@router.get("/{sprint_id}", response_model=SprintResponse)
def get_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific sprint by ID"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check if user has access to this sprint's project
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Check team membership for the project
        if current_user.role == UserRole.TEAM_LEADER:
            has_access = db.query(Team).filter(
                Team.team_leader_id == current_user.id,
                Team.projects.any(Project.id == project.id)
            ).first() is not None
        else:
            has_access = db.query(Team).filter(
                Team.members.any(User.id == current_user.id),
                Team.projects.any(Project.id == project.id)
            ).first() is not None
        
        if not has_access:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return sprint

@router.post("/", response_model=SprintResponse)
def create_sprint(
    sprint: SprintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new sprint"""
    # Check if project exists
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to create sprints in this project"
        )
    
    # Create sprint
    db_sprint = Sprint(**sprint.dict())
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint

@router.put("/{sprint_id}", response_model=SprintResponse)
def update_sprint(
    sprint_id: int,
    sprint_update: SprintUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this sprint"
        )
    
    # Update sprint fields
    update_data = sprint_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sprint, field, value)
    
    db.commit()
    db.refresh(sprint)
    return sprint

@router.delete("/{sprint_id}")
def delete_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this sprint"
        )
    
    # Check if sprint has tasks
    tasks_count = db.query(Task).filter(Task.sprint_id == sprint_id).count()
    if tasks_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete sprint with {tasks_count} task(s). Remove tasks first."
        )
    
    db.delete(sprint)
    db.commit()
    return {"message": "Sprint deleted successfully"}

@router.get("/{sprint_id}/tasks", response_model=List[TaskResponse])
def get_sprint_tasks(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks in a sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    tasks = db.query(Task).filter(Task.sprint_id == sprint_id).all()
    return tasks

# Bulk operations - these need to come BEFORE individual task operations
@router.post("/{sprint_id}/tasks/bulk")
def add_multiple_tasks_to_sprint(
    sprint_id: int,
    request: BulkTasksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add multiple tasks to sprint at once"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage this sprint"
        )
    
    # Get all tasks and validate they exist and belong to same project
    tasks = db.query(Task).filter(Task.id.in_(request.task_ids)).all()
    
    if len(tasks) != len(request.task_ids):
        found_ids = [t.id for t in tasks]
        missing_ids = [tid for tid in request.task_ids if tid not in found_ids]
        raise HTTPException(
            status_code=404,
            detail=f"Tasks not found: {missing_ids}"
        )
    
    # Verify all tasks belong to same project
    wrong_project_tasks = [t.id for t in tasks if t.project_id != sprint.project_id]
    if wrong_project_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Tasks {wrong_project_tasks} don't belong to the same project as sprint"
        )
    
    # Add all tasks to sprint
    added_count = 0
    already_in_sprint = []
    
    for task in tasks:
        if task.sprint_id != sprint_id:  # Only add if not already in this sprint
            task.sprint_id = sprint_id
            added_count += 1
        else:
            already_in_sprint.append(task.id)
    
    db.commit()
    
    result = {
        "message": f"Added {added_count} task(s) to sprint {sprint_id}",
        "added_count": added_count,
        "total_requested": len(request.task_ids)
    }
    
    if already_in_sprint:
        result["already_in_sprint"] = already_in_sprint
        result["message"] += f". {len(already_in_sprint)} task(s) were already in the sprint."
    
    return result

@router.delete("/{sprint_id}/tasks/bulk")
def remove_multiple_tasks_from_sprint(
    sprint_id: int,
    request: BulkTasksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove multiple tasks from sprint at once"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage this sprint"
        )
    
    # Get tasks that are currently in this sprint
    tasks_in_sprint = db.query(Task).filter(
        Task.id.in_(request.task_ids),
        Task.sprint_id == sprint_id
    ).all()
    
    if not tasks_in_sprint:
        raise HTTPException(
            status_code=404,
            detail="No specified tasks found in this sprint"
        )
    
    # Remove tasks from sprint
    removed_count = 0
    for task in tasks_in_sprint:
        task.sprint_id = None
        removed_count += 1
    
    db.commit()
    
    not_in_sprint = [tid for tid in request.task_ids if tid not in [t.id for t in tasks_in_sprint]]
    
    result = {
        "message": f"Removed {removed_count} task(s) from sprint {sprint_id}",
        "removed_count": removed_count,
        "total_requested": len(request.task_ids)
    }
    
    if not_in_sprint:
        result["not_in_sprint"] = not_in_sprint
        result["message"] += f". {len(not_in_sprint)} task(s) were not in the sprint."
    
    return result

# Individual task operations
@router.post("/{sprint_id}/tasks/{task_id}")
def add_task_to_sprint(
    sprint_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a task to sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage this sprint"
        )
    
    # Verify task belongs to same project as sprint
    if task.project_id != sprint.project_id:
        raise HTTPException(
            status_code=400,
            detail="Task must belong to the same project as the sprint"
        )
    
    task.sprint_id = sprint_id
    db.commit()
    db.refresh(task)
    return {"message": f"Task {task_id} added to sprint {sprint_id}"}

@router.delete("/{sprint_id}/tasks/{task_id}")
def remove_task_from_sprint(
    sprint_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove a task from sprint"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.sprint_id == sprint_id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in this sprint")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to manage this sprint"
        )
    
    task.sprint_id = None
    db.commit()
    db.refresh(task)
    return {"message": f"Task {task_id} removed from sprint {sprint_id}"}

@router.patch("/{sprint_id}/start")
def start_sprint(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start a sprint (change status from PLANNED to ACTIVE)"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not can_manage_sprints_in_project(current_user, project, db):
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to start sprints in this project"
        )
    
    from app.models.enums import SprintStatus
    if sprint.status != SprintStatus.PLANNED:
        raise HTTPException(
            status_code=400,
            detail="Only planned sprints can be started"
        )
    
    sprint.status = SprintStatus.ACTIVE
    db.commit()
    db.refresh(sprint)
    return sprint

@router.get("/{sprint_id}/statistics")
def get_sprint_statistics(
    sprint_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get sprint statistics and metrics"""
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Get all tasks in sprint
    tasks = db.query(Task).filter(Task.sprint_id == sprint_id).all()
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status.value == "done"])
    in_progress_tasks = len([t for t in tasks if t.status.value == "in_progress"])
    todo_tasks = len([t for t in tasks if t.status.value == "todo"])
    
    total_story_points = sum(t.story_points for t in tasks)
    completed_story_points = sum(t.story_points for t in tasks if t.status.value == "done")
    
    total_estimated_hours = sum(t.estimated_hours for t in tasks)
    total_actual_hours = sum(t.actual_hours for t in tasks)
    
    return {
        "sprint_id": sprint_id,
        "sprint_name": sprint.name,
        "sprint_status": sprint.status.value,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "todo_tasks": todo_tasks,
        "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
        "total_story_points": total_story_points,
        "completed_story_points": completed_story_points,
        "story_points_completion": (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0,
        "total_estimated_hours": total_estimated_hours,
        "total_actual_hours": total_actual_hours,
        "time_efficiency": (total_estimated_hours / total_actual_hours * 100) if total_actual_hours > 0 else 0
    }
