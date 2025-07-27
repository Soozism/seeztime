"""
Advanced query endpoints with time filtering
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.task import Task
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.milestone import Milestone
from app.models.team import Team
from app.models.time_log import TimeLog
from app.models.enums import UserRole
from app.schemas.task import TaskResponse
from app.schemas.project import ProjectResponse
from app.schemas.sprint import SprintResponse
from app.schemas.milestone import MilestoneResponse
from app.schemas.time_log import TimeLogResponse

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

def apply_time_filter(query, model, start_date: Optional[datetime], end_date: Optional[datetime]):
    """Apply time filter to query based on created_at field"""
    if start_date:
        query = query.filter(model.created_at >= start_date)
    if end_date:
        query = query.filter(model.created_at <= end_date)
    return query

# ============ TASK QUERIES ============

@router.get("/tasks/by-sprint/{sprint_id}", response_model=List[TaskResponse])
def get_tasks_by_sprint(
    sprint_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks for a specific sprint with time filtering"""
    # Check if sprint exists and user has access
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check project access through sprint
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this sprint")
    
    query = db.query(Task).filter(Task.sprint_id == sprint_id)
    query = apply_time_filter(query, Task, start_date, end_date)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.get("/tasks/by-user/{user_id}", response_model=List[TaskResponse])
def get_tasks_by_user(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks assigned to a specific user with time filtering"""
    # Check if user can access these tasks (admin/PM can see all, others only their own)
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to other user's tasks")
    
    query = db.query(Task).filter(Task.assignee_id == user_id)
    query = apply_time_filter(query, Task, start_date, end_date)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

# ============ SPRINT QUERIES ============

@router.get("/sprints/by-project/{project_id}", response_model=List[SprintResponse])
def get_sprints_by_project(
    project_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sprints for a specific project with time filtering"""
    # Check project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    query = db.query(Sprint).filter(Sprint.project_id == project_id)
    query = apply_time_filter(query, Sprint, start_date, end_date)
    
    sprints = query.offset(skip).limit(limit).all()
    return sprints

@router.get("/sprints/by-user/{user_id}", response_model=List[SprintResponse])
def get_sprints_by_user(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sprints where user has tasks assigned with time filtering"""
    # Check access permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to other user's sprints")
    
    # Get sprints where user has assigned tasks
    query = db.query(Sprint).join(Task).filter(Task.assignee_id == user_id)
    query = apply_time_filter(query, Sprint, start_date, end_date)
    
    sprints = query.distinct().offset(skip).limit(limit).all()
    return sprints

# ============ PROJECT QUERIES ============

@router.get("/projects/by-user/{user_id}", response_model=List[ProjectResponse])
def get_projects_by_user(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all projects where user is involved (through team membership or tasks)"""
    # Check access permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to other user's projects")
    
    # Get projects through team membership
    team_projects = db.query(Project).join(Team.projects).join(Team.members).filter(User.id == user_id)
    
    # Get projects through task assignment
    task_projects = db.query(Project).join(Task).filter(Task.assignee_id == user_id)
    
    # Combine both queries
    query = team_projects.union(task_projects)
    query = apply_time_filter(query, Project, start_date, end_date)
    
    projects = query.offset(skip).limit(limit).all()
    return projects

# ============ TIME LOG QUERIES ============

@router.get("/time-logs/by-user/{user_id}", response_model=List[TimeLogResponse])
def get_time_logs_by_user(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by log date"),
    end_date: Optional[datetime] = Query(None, description="Filter by log date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all time logs for a specific user with time filtering"""
    # Check access permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to other user's time logs")
    
    query = db.query(TimeLog).filter(TimeLog.user_id == user_id)
    
    # For time logs, filter by date field instead of created_at
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    time_logs = query.offset(skip).limit(limit).all()
    return time_logs

@router.get("/time-logs/by-task/{task_id}", response_model=List[TimeLogResponse])
def get_time_logs_by_task(
    task_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by log date"),
    end_date: Optional[datetime] = Query(None, description="Filter by log date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all time logs for a specific task with time filtering"""
    # Check if task exists and user has access
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check project access through task
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this task")
    
    query = db.query(TimeLog).filter(TimeLog.task_id == task_id)
    
    # Filter by date field
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    time_logs = query.offset(skip).limit(limit).all()
    return time_logs

@router.get("/time-logs/by-sprint/{sprint_id}", response_model=List[TimeLogResponse])
def get_time_logs_by_sprint(
    sprint_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by log date"),
    end_date: Optional[datetime] = Query(None, description="Filter by log date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all time logs for tasks in a specific sprint with time filtering"""
    # Check if sprint exists and user has access
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check project access through sprint
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this sprint")
    
    # Get time logs through tasks in the sprint
    query = db.query(TimeLog).join(Task).filter(Task.sprint_id == sprint_id)
    
    # Filter by date field
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    time_logs = query.offset(skip).limit(limit).all()
    return time_logs

@router.get("/time-logs/by-project/{project_id}", response_model=List[TimeLogResponse])
def get_time_logs_by_project(
    project_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by log date"),
    end_date: Optional[datetime] = Query(None, description="Filter by log date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all time logs for tasks in a specific project with time filtering"""
    # Check project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get time logs through tasks in the project
    query = db.query(TimeLog).join(Task).filter(Task.project_id == project_id)
    
    # Filter by date field
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    time_logs = query.offset(skip).limit(limit).all()
    return time_logs

# ============ MILESTONE QUERIES ============

@router.get("/milestones/by-sprint/{sprint_id}", response_model=List[MilestoneResponse])
def get_milestones_by_sprint(
    sprint_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all milestones for a specific sprint with time filtering"""
    # Check if sprint exists and user has access
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check project access through sprint
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this sprint")
    
    query = db.query(Milestone).filter(Milestone.sprint_id == sprint_id)
    query = apply_time_filter(query, Milestone, start_date, end_date)
    
    milestones = query.offset(skip).limit(limit).all()
    return milestones

@router.get("/milestones/by-project/{project_id}", response_model=List[MilestoneResponse])
def get_milestones_by_project(
    project_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all milestones for a specific project with time filtering"""
    # Check project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get milestones through sprints in the project
    query = db.query(Milestone).join(Sprint).filter(Sprint.project_id == project_id)
    query = apply_time_filter(query, Milestone, start_date, end_date)
    
    milestones = query.offset(skip).limit(limit).all()
    return milestones

# ============ SUMMARY/AGGREGATION ENDPOINTS ============

@router.get("/summary/user/{user_id}/time-logs")
def get_user_time_summary(
    user_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time log summary for a user"""
    # Check access permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied to other user's summary")
    
    query = db.query(func.sum(TimeLog.hours)).filter(TimeLog.user_id == user_id)
    
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    total_hours = query.scalar() or 0
    
    return {
        "user_id": user_id,
        "total_hours": float(total_hours),
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/summary/project/{project_id}/time-logs")
def get_project_time_summary(
    project_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time log summary for a project"""
    # Check project access
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    query = db.query(func.sum(TimeLog.hours)).join(Task).filter(Task.project_id == project_id)
    
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    total_hours = query.scalar() or 0
    
    return {
        "project_id": project_id,
        "total_hours": float(total_hours),
        "start_date": start_date,
        "end_date": end_date
    }

@router.get("/summary/sprint/{sprint_id}/time-logs")
def get_sprint_time_summary(
    sprint_id: int,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time log summary for a sprint"""
    # Check if sprint exists and user has access
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint:
        raise HTTPException(status_code=404, detail="Sprint not found")
    
    # Check project access through sprint
    project = db.query(Project).filter(Project.id == sprint.project_id).first()
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Access denied to this sprint")
    
    query = db.query(func.sum(TimeLog.hours)).join(Task).filter(Task.sprint_id == sprint_id)
    
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    total_hours = query.scalar() or 0
    
    return {
        "sprint_id": sprint_id,
        "total_hours": float(total_hours),
        "start_date": start_date,
        "end_date": end_date
    }
