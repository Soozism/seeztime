"""
Dashboard and reporting endpoints
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.team import Team
from app.models.project import Project
from app.models.task import Task
from app.models.sprint import Sprint
from app.models.time_log import TimeLog
from app.models.enums import TaskStatus, ProjectStatus, SprintStatus, UserRole

router = APIRouter()

def can_access_user_data(current_user: User, target_user_id: int, db: Session) -> bool:
    """Check if current user can access target user's data"""
    # Admins and project managers can access everyone's data
    if current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    
    # Users can access their own data
    if current_user.id == target_user_id:
        return True
    
    # Team leaders can access their team members' data
    if current_user.role == UserRole.TEAM_LEADER:
        # Check if target user is in any team led by current user
        led_teams = db.query(Team).filter(Team.team_leader_id == current_user.id).all()
        for team in led_teams:
            if any(member.id == target_user_id for member in team.members):
                return True
    
    return False

@router.get("/dashboard")
def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get comprehensive dashboard data for the current user"""
    
    # Get user's teams and projects
    user_teams = db.query(Team).filter(
        (Team.team_leader_id == current_user.id) | 
        (Team.members.any(User.id == current_user.id))
    ).all()
    
    # Get projects user has access to (through teams or direct assignment)
    user_projects_query = db.query(Project)
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Filter to projects accessible through teams
        team_ids = [team.id for team in user_teams]
        if team_ids:
            user_projects_query = user_projects_query.join(Team.projects).filter(Team.id.in_(team_ids))
        else:
            user_projects_query = user_projects_query.filter(False)  # No access
    
    user_projects = user_projects_query.all()
    project_ids = [p.id for p in user_projects]
    
    # Project statistics
    total_projects = len(user_projects)
    active_projects = len([p for p in user_projects if p.status == ProjectStatus.ACTIVE])
    
    # Task statistics - both assigned and in accessible projects
    my_assigned_tasks = db.query(Task).filter(Task.assignee_id == current_user.id).all()
    
    if project_ids:
        accessible_tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all()
    else:
        accessible_tasks = []
    
    # My task counts by status
    my_todo = len([t for t in my_assigned_tasks if t.status == TaskStatus.TODO])
    my_in_progress = len([t for t in my_assigned_tasks if t.status == TaskStatus.IN_PROGRESS])
    my_review = len([t for t in my_assigned_tasks if t.status == TaskStatus.REVIEW])
    my_done = len([t for t in my_assigned_tasks if t.status == TaskStatus.DONE])
    my_blocked = len([t for t in my_assigned_tasks if t.status == TaskStatus.BLOCKED])
    
    # Story points statistics
    my_total_story_points = sum(t.story_points or 0 for t in my_assigned_tasks)
    my_completed_story_points = sum(t.story_points or 0 for t in my_assigned_tasks if t.status == TaskStatus.DONE)
    
    # Sprint statistics
    if project_ids:
        my_sprints = db.query(Sprint).filter(Sprint.project_id.in_(project_ids)).all()
        active_sprints = len([s for s in my_sprints if s.status == SprintStatus.ACTIVE])
        total_sprints = len(my_sprints)
    else:
        active_sprints = total_sprints = 0
    
    # Time log statistics
    total_hours = db.query(func.sum(TimeLog.hours)).filter(
        TimeLog.user_id == current_user.id
    ).scalar() or 0
    
    # Recent time logs
    recent_time_logs = db.query(TimeLog).filter(
        TimeLog.user_id == current_user.id
    ).order_by(TimeLog.created_at.desc()).limit(5).all()
    
    # Recent tasks
    recent_tasks = db.query(Task).filter(
        Task.assignee_id == current_user.id
    ).order_by(Task.updated_at.desc()).limit(5).all()
    
    # Team information
    team_info = []
    for team in user_teams:
        team_info.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "is_leader": team.team_leader_id == current_user.id,
            "member_count": len(team.members),
            "project_count": len(team.projects)
        })
    
    return {
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role.value,
            "email": current_user.email
        },
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "accessible_projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status.value
                } for p in user_projects[:10]  # Limit to 10 for dashboard
            ]
        },
        "tasks": {
            "my_assigned_total": len(my_assigned_tasks),
            "my_todo": my_todo,
            "my_in_progress": my_in_progress,
            "my_review": my_review,
            "my_completed": my_done,
            "my_blocked": my_blocked,
            "accessible_total": len(accessible_tasks)
        },
        "story_points": {
            "my_total": my_total_story_points,
            "my_completed": my_completed_story_points,
            "completion_rate": (my_completed_story_points / my_total_story_points * 100) if my_total_story_points > 0 else 0
        },
        "sprints": {
            "total": total_sprints,
            "active": active_sprints
        },
        "time_logs": {
            "total_hours": float(total_hours),
            "recent_logs": [
                {
                    "id": log.id,
                    "description": log.description,
                    "hours": log.hours,
                    "date": log.date,
                    "task_id": log.task_id
                } for log in recent_time_logs
            ]
        },
        "teams": {
            "total": len(user_teams),
            "leading": len([t for t in user_teams if t.team_leader_id == current_user.id]),
            "team_details": team_info
        },
        "recent_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value,
                "story_points": task.story_points,
                "project_name": task.project.name if task.project else None
            } for task in recent_tasks
        ]
    }

@router.get("/dashboard/user/{user_id}")
def get_user_dashboard_data(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get comprehensive dashboard data for a specific user (with permission checks)"""
    
    # Check permissions
    if not can_access_user_data(current_user, user_id, db):
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only view your own data or your team members' data."
        )
    
    # Get target user
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's teams and projects
    user_teams = db.query(Team).filter(
        (Team.team_leader_id == target_user.id) | 
        (Team.members.any(User.id == target_user.id))
    ).all()
    
    # Get projects user has access to (through teams or direct assignment)
    user_projects_query = db.query(Project)
    if target_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Filter to projects accessible through teams
        team_ids = [team.id for team in user_teams]
        if team_ids:
            user_projects_query = user_projects_query.join(Team.projects).filter(Team.id.in_(team_ids))
        else:
            user_projects_query = user_projects_query.filter(False)  # No access
    
    user_projects = user_projects_query.all()
    project_ids = [p.id for p in user_projects]
    
    # Project statistics
    total_projects = len(user_projects)
    active_projects = len([p for p in user_projects if p.status == ProjectStatus.ACTIVE])
    
    # Task statistics - both assigned and in accessible projects
    assigned_tasks = db.query(Task).filter(Task.assignee_id == target_user.id).all()
    created_tasks = db.query(Task).filter(Task.created_by_id == target_user.id).all()
    
    if project_ids:
        accessible_tasks = db.query(Task).filter(Task.project_id.in_(project_ids)).all()
    else:
        accessible_tasks = []
    
    # Task counts by status
    assigned_todo = len([t for t in assigned_tasks if t.status == TaskStatus.TODO])
    assigned_in_progress = len([t for t in assigned_tasks if t.status == TaskStatus.IN_PROGRESS])
    assigned_review = len([t for t in assigned_tasks if t.status == TaskStatus.REVIEW])
    assigned_done = len([t for t in assigned_tasks if t.status == TaskStatus.DONE])
    assigned_blocked = len([t for t in assigned_tasks if t.status == TaskStatus.BLOCKED])
    
    # Story points statistics
    total_story_points = sum(t.story_points or 0 for t in assigned_tasks)
    completed_story_points = sum(t.story_points or 0 for t in assigned_tasks if t.status == TaskStatus.DONE)
    
    # Sprint statistics
    if project_ids:
        user_sprints = db.query(Sprint).filter(Sprint.project_id.in_(project_ids)).all()
        active_sprints = len([s for s in user_sprints if s.status == SprintStatus.ACTIVE])
        total_sprints = len(user_sprints)
    else:
        active_sprints = total_sprints = 0
    
    # Time log statistics
    total_hours = db.query(func.sum(TimeLog.hours)).filter(
        TimeLog.user_id == target_user.id
    ).scalar() or 0
    
    # Recent time logs (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_hours = db.query(func.sum(TimeLog.hours)).filter(
        TimeLog.user_id == target_user.id,
        TimeLog.date >= thirty_days_ago
    ).scalar() or 0
    
    # Time logs grouped by project
    time_by_project = db.query(
        Project.name,
        func.sum(TimeLog.hours).label('total_hours')
    ).select_from(TimeLog).join(Task).join(Project).filter(
        TimeLog.user_id == target_user.id
    ).group_by(Project.id, Project.name).all()
    
    # Recent tasks and time logs
    recent_tasks = db.query(Task).filter(
        Task.assignee_id == target_user.id
    ).order_by(Task.updated_at.desc()).limit(10).all()
    
    recent_time_logs = db.query(TimeLog).filter(
        TimeLog.user_id == target_user.id
    ).order_by(TimeLog.created_at.desc()).limit(10).all()
    
    # Team information with detailed stats
    team_info = []
    for team in user_teams:
        team_info.append({
            "id": team.id,
            "name": team.name,
            "description": team.description,
            "is_leader": team.team_leader_id == target_user.id,
            "member_count": len(team.members),
            "project_count": len(team.projects),
            "projects": [{"id": p.id, "name": p.name} for p in team.projects]
        })
    
    # Performance metrics
    avg_hours_per_task = (total_hours / len(assigned_tasks)) if assigned_tasks else 0
    completion_rate = (assigned_done / len(assigned_tasks) * 100) if assigned_tasks else 0
    
    return {
        "user_info": {
            "id": target_user.id,
            "username": target_user.username,
            "full_name": target_user.full_name,
            "role": target_user.role.value,
            "email": target_user.email,
            "is_active": target_user.is_active,
            "created_at": target_user.created_at
        },
        "projects": {
            "total": total_projects,
            "active": active_projects,
            "accessible_projects": [
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status.value,
                    "start_date": p.start_date,
                    "end_date": p.end_date
                } for p in user_projects
            ]
        },
        "tasks": {
            "assigned_total": len(assigned_tasks),
            "created_total": len(created_tasks),
            "assigned_todo": assigned_todo,
            "assigned_in_progress": assigned_in_progress,
            "assigned_review": assigned_review,
            "assigned_completed": assigned_done,
            "assigned_blocked": assigned_blocked,
            "accessible_total": len(accessible_tasks),
            "completion_rate": completion_rate
        },
        "story_points": {
            "total_assigned": total_story_points,
            "completed": completed_story_points,
            "completion_rate": (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0,
            "average_per_task": (total_story_points / len(assigned_tasks)) if assigned_tasks else 0
        },
        "sprints": {
            "total": total_sprints,
            "active": active_sprints,
            "accessible_sprints": [
                {
                    "id": s.id,
                    "name": s.name,
                    "status": s.status.value,
                    "project_name": s.project.name
                } for s in user_sprints[:10]  # Limit to 10
            ]
        },
        "time_logs": {
            "total_hours": float(total_hours),
            "recent_30_days_hours": float(recent_hours),
            "average_hours_per_task": float(avg_hours_per_task),
            "hours_by_project": [
                {
                    "project_name": project_name,
                    "hours": float(hours)
                } for project_name, hours in time_by_project
            ],
            "recent_logs": [
                {
                    "id": log.id,
                    "description": log.description,
                    "hours": log.hours,
                    "date": log.date,
                    "task_id": log.task_id,
                    "task_title": log.task.title if log.task else None
                } for log in recent_time_logs
            ]
        },
        "teams": {
            "total": len(user_teams),
            "leading": len([t for t in user_teams if t.team_leader_id == target_user.id]),
            "team_details": team_info
        },
        "recent_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value,
                "story_points": task.story_points,
                "project_name": task.project.name if task.project else None,
                "due_date": task.due_date,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours
            } for task in recent_tasks
        ],
        "performance_metrics": {
            "completion_rate": completion_rate,
            "average_hours_per_task": float(avg_hours_per_task),
            "tasks_per_project": len(assigned_tasks) / max(total_projects, 1),
            "story_points_velocity": completed_story_points  # Could be enhanced with sprint-based calculation
        }
    }

@router.get("/reports/project/{project_id}")
def get_project_report(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get detailed report for a specific project"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Task statistics by status
    task_stats = db.query(Task.status, func.count(Task.id)).filter(
        Task.project_id == project_id
    ).group_by(Task.status).all()
    
    # Total story points
    total_story_points = db.query(func.sum(Task.story_points)).filter(
        Task.project_id == project_id
    ).scalar() or 0
    
    completed_story_points = db.query(func.sum(Task.story_points)).filter(
        Task.project_id == project_id,
        Task.status == TaskStatus.DONE
    ).scalar() or 0
    
    # Time tracking
    total_estimated_hours = db.query(func.sum(Task.estimated_hours)).filter(
        Task.project_id == project_id
    ).scalar() or 0
    
    total_actual_hours = db.query(func.sum(Task.actual_hours)).filter(
        Task.project_id == project_id
    ).scalar() or 0
    
    # Sprint information
    sprints = db.query(Sprint).filter(Sprint.project_id == project_id).all()
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "status": project.status.value,
            "start_date": project.start_date,
            "end_date": project.end_date
        },
        "tasks": {
            "by_status": {status.value: count for status, count in task_stats},
            "story_points": {
                "total": total_story_points,
                "completed": completed_story_points,
                "completion_rate": (completed_story_points / total_story_points * 100) if total_story_points > 0 else 0
            }
        },
        "time_tracking": {
            "estimated_hours": float(total_estimated_hours),
            "actual_hours": float(total_actual_hours),
            "efficiency": (total_estimated_hours / total_actual_hours * 100) if total_actual_hours > 0 else 0
        },
        "sprints": [
            {
                "id": sprint.id,
                "name": sprint.name,
                "status": sprint.status.value,
                "start_date": sprint.start_date,
                "end_date": sprint.end_date
            } for sprint in sprints
        ]
    }

@router.get("/kanban/{project_id}")
def get_kanban_board(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get kanban board data for a project"""
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get tasks grouped by status
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    kanban_data = {
        "todo": [],
        "in_progress": [],
        "review": [],
        "done": [],
        "blocked": []
    }
    
    for task in tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "story_points": task.story_points,
            "assignee": {
                "id": task.assignee.id,
                "username": task.assignee.username,
                "full_name": task.assignee.full_name
            } if task.assignee else None,
            "due_date": task.due_date
        }
        
        if task.status == TaskStatus.TODO:
            kanban_data["todo"].append(task_data)
        elif task.status == TaskStatus.IN_PROGRESS:
            kanban_data["in_progress"].append(task_data)
        elif task.status == TaskStatus.REVIEW:
            kanban_data["review"].append(task_data)
        elif task.status == TaskStatus.DONE:
            kanban_data["done"].append(task_data)
        elif task.status == TaskStatus.BLOCKED:
            kanban_data["blocked"].append(task_data)
    
    return {
        "project": {
            "id": project.id,
            "name": project.name
        },
        "columns": kanban_data
    }
