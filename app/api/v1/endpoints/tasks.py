"""
Task management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.team import Team
from app.models.time_log import TimeLog
from app.models.active_timer import ActiveTimer
from app.models.enums import UserRole, SprintStatus
from app.models.sprint import Sprint
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate

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

def can_create_tasks_in_project(user: User, project: Project, db: Session) -> bool:
    """Check if user can create tasks in project"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    
    # Team leaders can create tasks in their assigned projects
    if user.role == UserRole.TEAM_LEADER:
        return db.query(Team).filter(
            Team.team_leader_id == user.id,
            Team.projects.any(Project.id == project.id)
        ).first() is not None
    
    return False

@router.get("/", response_model=List[TaskResponse])
def get_tasks(
    skip: int = 0,
    limit: int = 100,
    project_id: int = None,
    assignee_id: int = None,
    expand: bool = True,
    only_main_tasks: bool = True,
    sprint_done: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks with optional filters and expanded details"""
    from sqlalchemy.orm import joinedload
    
    if expand:
        # Load with related objects
        query = db.query(Task).options(
            joinedload(Task.project),
            joinedload(Task.assignee),
            joinedload(Task.created_by),
            joinedload(Task.sprint)
        )
    else:
        query = db.query(Task)
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if only_main_tasks:
        query = query.filter((Task.is_subtask == False) | (Task.parent_task_id == None))

    # Filter based on sprint completion status
    if sprint_done:
        # Only tasks whose sprint is completed
        query = query.filter(Task.sprint_id.isnot(None)).filter(
            Task.sprint.has(Sprint.status == SprintStatus.COMPLETED)
        )
    else:
        # Exclude tasks whose sprint is completed
        query = query.filter(
            (Task.sprint_id.is_(None)) | (Task.sprint.has(Sprint.status != SprintStatus.COMPLETED))
        )

    # Order by creation date (newest first) and then by priority (higher priority first)
    query = query.order_by(Task.created_at.desc(), Task.priority.desc())

    tasks = query.offset(skip).limit(limit).all()
    
    # Convert to response objects with expansions if requested
    if expand:
        return [TaskResponse.from_orm_with_expansions(task) for task in tasks]
    else:
        return tasks

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    expand: bool = True,
    include_time_logs: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task by ID with optional expanded details and time logs"""
    from sqlalchemy.orm import joinedload
    from datetime import datetime
    
    if expand:
        task = db.query(Task).options(
            joinedload(Task.project),
            joinedload(Task.assignee),
            joinedload(Task.created_by),
            joinedload(Task.sprint)
        ).filter(Task.id == task_id).first()
    else:
        task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get expanded response
    if expand:
        response_data = TaskResponse.from_orm_with_expansions(task).__dict__
    else:
        response_data = TaskResponse.from_orm(task).__dict__
    
    # Include time logs if requested
    if include_time_logs:
        # Get time logs for this task
        time_logs = db.query(TimeLog).filter(TimeLog.task_id == task_id).all()
        time_logs_data = []
        for log in time_logs:
            time_log_data = {
                "id": log.id,
                "description": log.description,
                "hours": log.hours,
                "date": log.date,
                "user_id": log.user_id,
                "created_at": log.created_at,
                "updated_at": log.updated_at
            }
            # Add user info if available
            if hasattr(log, 'user') and log.user:
                time_log_data["user_username"] = log.user.username
                if log.user.first_name:
                    time_log_data["user_name"] = f"{log.user.first_name} {log.user.last_name}" if log.user.last_name else log.user.first_name
            time_logs_data.append(time_log_data)
        
        response_data["time_logs"] = time_logs_data
        
        # Check for active timer
        active_timer = db.query(ActiveTimer).filter(
            ActiveTimer.task_id == task_id,
            ActiveTimer.is_active.is_(True)
        ).first()
        
        if active_timer:
            elapsed_seconds = int((datetime.utcnow() - active_timer.start_time).total_seconds())
            response_data["active_timer"] = {
                "id": active_timer.id,
                "user_id": active_timer.user_id,
                "start_time": active_timer.start_time,
                "elapsed_seconds": elapsed_seconds,
                "elapsed_hours": round(elapsed_seconds / 3600, 2)
            }
    # Add subtasks to response
    subtasks = db.query(Task).filter(Task.parent_task_id == task_id, Task.is_subtask.is_(True)).all()
    if expand:
        response_data["subtasks"] = [TaskResponse.from_orm_with_expansions(subtask).__dict__ for subtask in subtasks]
    else:
        response_data["subtasks"] = [TaskResponse.from_orm(subtask).__dict__ for subtask in subtasks]
    
    return TaskResponse(**response_data)

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    expand: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new task (Team leaders can create tasks in their assigned projects)"""
    from sqlalchemy.orm import joinedload
    
    # Verify project exists
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user can create tasks in this project
    # Developers can only create tasks for themselves
    if current_user.role == UserRole.DEVELOPER:
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Developers can only create tasks assigned to themselves."
            )
    elif current_user.role == UserRole.TEAM_LEADER:
        # Team leaders can create tasks for users in their team
        team = db.query(Team).filter(
            Team.team_leader_id == current_user.id,
            Team.projects.any(Project.id == project.id)
        ).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a team leader for this project."
            )
        # Check if assignee is in the team
        member_ids = [member.id for member in team.members]
        if task.assignee_id not in member_ids and task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team leaders can only create tasks for users in their team."
            )
    elif not can_create_tasks_in_project(current_user, project, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create tasks in this project"
        )
    
    task_data = task.dict()
    # اگر parent_task_id برابر 0 بود، مقدار None قرار بده
    if 'parent_task_id' in task_data and task_data['parent_task_id'] == 0:
        task_data['parent_task_id'] = None
    db_task = Task(
        **task_data,
        created_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    # Reload with relationships if expand is requested
    if expand:
        db_task = db.query(Task).options(
            joinedload(Task.project),
            joinedload(Task.assignee),
            joinedload(Task.created_by),
            joinedload(Task.sprint)
        ).filter(Task.id == db_task.id).first()
        return TaskResponse.from_orm_with_expansions(db_task)
    else:
        return TaskResponse.from_orm(db_task)

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    expand: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update task"""
    from sqlalchemy.orm import joinedload
    
    if expand:
        task = db.query(Task).options(
            joinedload(Task.project),
            joinedload(Task.assignee),
            joinedload(Task.created_by),
            joinedload(Task.sprint)
        ).filter(Task.id == task_id).first()
    else:
        task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if current_user.role == UserRole.DEVELOPER:
        # Developers can update tasks they created or are assigned to
        if not (task.created_by_id == current_user.id or task.assignee_id == current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Developers can only update tasks they created or are assigned to."
            )
    elif current_user.role == UserRole.TEAM_LEADER:
        # Team leaders can update tasks for users in their team
        team = db.query(Team).filter(
            Team.team_leader_id == current_user.id,
            Team.projects.any(Project.id == project.id)
        ).first()
        if not team:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a team leader for this project."
            )
        member_ids = [member.id for member in team.members]
        if not (
            task.assignee_id in member_ids or
            task.created_by_id in member_ids or
            task.assignee_id == current_user.id or
            task.created_by_id == current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Team leaders can only update tasks for users in their team."
            )
    elif not (
        current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] or
        can_create_tasks_in_project(current_user, project, db) or
        task.assignee_id == current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task"
        )
    
    update_data = task_update.dict(exclude_unset=True)
    # اگر parent_task_id برابر 0 بود، مقدار None قرار بده
    if 'parent_task_id' in update_data and update_data['parent_task_id'] == 0:
        update_data['parent_task_id'] = None
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    # Return properly formatted response
    if expand:
        return TaskResponse.from_orm_with_expansions(task)
    else:
        return TaskResponse.from_orm(task)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions - only admins, project managers, or team leaders can delete tasks
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not (
        current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] or
        can_create_tasks_in_project(current_user, project, db)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )
    
    # حذف همه ساب‌تسک‌های این تسک
    subtasks = db.query(Task).filter(Task.parent_task_id == task_id).all()
    for subtask in subtasks:
        db.delete(subtask)
    db.delete(task)
    db.commit()
    return {"message": "Task and its subtasks deleted successfully"}

@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update task status"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions - assignees can update status of their own tasks, 
    # or team leaders/managers can update any task in their projects
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not (
        task.assignee_id == current_user.id or
        current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] or
        can_create_tasks_in_project(current_user, project, db)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task status"
        )
    
    task.status = status_update.status
    # تغییر وضعیت همه ساب‌تسک‌های این تسک
    subtasks = db.query(Task).filter(Task.parent_task_id == task_id).all()
    for subtask in subtasks:
        subtask.status = status_update.status
    db.commit()
    db.refresh(task)
    return task


# Subtask endpoints (using the new is_subtask field)
@router.get("/{task_id}/subtasks", response_model=List[TaskResponse])
def get_task_subtasks(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all subtasks for a task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check project access
    if not check_team_project_access(current_user, task.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    subtasks = db.query(Task).filter(
        Task.parent_task_id == task_id,
        Task.is_subtask
    ).all()
    return subtasks
