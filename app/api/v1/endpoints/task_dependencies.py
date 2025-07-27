"""
Task Dependency management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.task import Task
from app.models.task_dependency import TaskDependency
from app.models.project import Project
from app.models.team import Team
from app.models.enums import UserRole
from app.schemas.task_dependency import TaskDependencyCreate, TaskDependencyResponse

router = APIRouter()

def check_team_project_access(user: User, project: Project, db: Session) -> bool:
    """Check if user has access to project through team membership"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    
    # Check if user is team leader of any team assigned to the project
    team_leader_access = db.query(Team).filter(
        Team.team_leader_id == user.id,
        Team.projects.any(Project.id == project.id)
    ).first()
    if team_leader_access:
        return True
    
    # Check if user is a member of any team assigned to the project
    member_access = db.query(Team).join(Team.members).filter(
        User.id == user.id,
        Team.projects.any(Project.id == project.id)
    ).first()
    if member_access:
        return True
    
    return False

@router.get("/task/{task_id}/dependencies", response_model=List[TaskDependencyResponse])
def get_task_dependencies(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all dependencies for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check project access
    if not check_team_project_access(current_user, task.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    dependencies = db.query(TaskDependency).filter(TaskDependency.task_id == task_id).all()
    return dependencies

@router.post("/task/{task_id}/dependencies", response_model=TaskDependencyResponse)
def create_task_dependency(
    task_id: int,
    dependency: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new task dependency"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    depends_on_task = db.query(Task).filter(Task.id == dependency.depends_on_task_id).first()
    if not depends_on_task:
        raise HTTPException(status_code=404, detail="Dependency task not found")
    
    # Check project access for both tasks
    if not check_team_project_access(current_user, task.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if not check_team_project_access(current_user, depends_on_task.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions for dependency task")
    
    # Check if dependency already exists
    existing = db.query(TaskDependency).filter(
        TaskDependency.task_id == task_id,
        TaskDependency.depends_on_task_id == dependency.depends_on_task_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Dependency already exists")
    
    # Prevent circular dependencies
    if task_id == dependency.depends_on_task_id:
        raise HTTPException(status_code=400, detail="Task cannot depend on itself")
    
    db_dependency = TaskDependency(
        task_id=task_id,
        depends_on_task_id=dependency.depends_on_task_id
    )
    db.add(db_dependency)
    db.commit()
    db.refresh(db_dependency)
    return db_dependency

@router.delete("/task/{task_id}/dependencies/{dependency_id}")
def delete_task_dependency(
    task_id: int,
    dependency_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a task dependency"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    dependency = db.query(TaskDependency).filter(
        TaskDependency.id == dependency_id,
        TaskDependency.task_id == task_id
    ).first()
    if not dependency:
        raise HTTPException(status_code=404, detail="Dependency not found")
    
    # Check project access
    if not check_team_project_access(current_user, task.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(dependency)
    db.commit()
    return {"message": "Dependency deleted successfully"}
