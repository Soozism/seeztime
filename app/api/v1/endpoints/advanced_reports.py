"""
Advanced reporting endpoints with data export capabilities
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, date, timedelta
import io
import csv
import json

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.team import Team
from app.models.time_log import TimeLog
from app.models.completed_sp import CompletedStoryPoints
from app.models.enums import UserRole, TaskStatus

router = APIRouter()

@router.get("/productivity-summary")
def get_productivity_summary(
    period: str = Query("week", description="Period: day, week, month, quarter, year"),
    team_id: Optional[int] = Query(None, description="Filter by team"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get productivity summary with different time periods"""
    
    # Calculate date range based on period
    now = datetime.now()
    if period == "day":
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "quarter":
        quarter_start_month = ((now.month - 1) // 3) * 3 + 1
        start_date = now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "year":
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = now - timedelta(days=7)  # Default to week
    
    # Get accessible projects
    from app.api.v1.endpoints.reports import get_accessible_projects
    accessible_projects = get_accessible_projects(current_user, db)
    
    # Base queries
    time_logs_query = db.query(TimeLog).join(Task).filter(
        Task.project_id.in_(accessible_projects),
        TimeLog.start_time >= start_date
    )
    
    completed_sp_query = db.query(CompletedStoryPoints).filter(
        CompletedStoryPoints.project_id.in_(accessible_projects),
        CompletedStoryPoints.completed_at >= start_date
    )
    
    # Apply filters
    if team_id:
        team_user_ids = db.query(User.id).join(Team.members).filter(Team.id == team_id).all()
        user_ids = [uid[0] for uid in team_user_ids]
        time_logs_query = time_logs_query.filter(TimeLog.user_id.in_(user_ids))
        completed_sp_query = completed_sp_query.filter(CompletedStoryPoints.user_id.in_(user_ids))
    
    if project_id:
        time_logs_query = time_logs_query.filter(Task.project_id == project_id)
        completed_sp_query = completed_sp_query.filter(CompletedStoryPoints.project_id == project_id)
    
    # Execute queries
    time_logs = time_logs_query.all()
    completed_points = completed_sp_query.all()
    
    # Calculate metrics
    total_hours = sum(log.duration_minutes or 0 for log in time_logs) / 60
    total_story_points = sum(cp.story_points for cp in completed_points)
    unique_users = len(set(log.user_id for log in time_logs))
    unique_projects = len(set(log.task.project_id for log in time_logs if log.task))
    
    # Velocity calculation (story points per day)
    days_in_period = (now - start_date).days + 1
    velocity = total_story_points / days_in_period if days_in_period > 0 else 0
    
    # Efficiency (story points per hour)
    efficiency = total_story_points / total_hours if total_hours > 0 else 0
    
    return {
        "period": period,
        "date_range": {
            "start": start_date.isoformat(),
            "end": now.isoformat()
        },
        "metrics": {
            "total_hours": round(total_hours, 2),
            "total_story_points": total_story_points,
            "velocity_per_day": round(velocity, 2),
            "efficiency_points_per_hour": round(efficiency, 2),
            "active_users": unique_users,
            "active_projects": unique_projects,
            "avg_hours_per_user": round(total_hours / unique_users, 2) if unique_users > 0 else 0
        },
        "applied_filters": {
            "team_id": team_id,
            "project_id": project_id
        }
    }

@router.get("/burndown-chart")
def get_burndown_chart(
    project_id: int = Query(..., description="Project ID for burndown chart"),
    sprint_id: Optional[int] = Query(None, description="Optional sprint ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get burndown chart data for project or sprint"""
    
    # Verify access to project
    from app.api.v1.endpoints.reports import get_accessible_projects
    accessible_projects = get_accessible_projects(current_user, db)
    
    if project_id not in accessible_projects:
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Base query for tasks
    tasks_query = db.query(Task).filter(Task.project_id == project_id)
    if sprint_id:
        tasks_query = tasks_query.filter(Task.sprint_id == sprint_id)
    
    tasks = tasks_query.all()
    
    # Calculate total story points
    total_story_points = sum(task.story_points or 0 for task in tasks)
    
    # Get completion dates
    completed_story_points = db.query(CompletedStoryPoints).filter(
        CompletedStoryPoints.project_id == project_id
    ).order_by(CompletedStoryPoints.completed_at).all()
    
    if sprint_id:
        # Filter by sprint tasks
        sprint_task_ids = [task.id for task in tasks]
        completed_story_points = [
            cp for cp in completed_story_points 
            if cp.task_id in sprint_task_ids
        ]
    
    # Generate burndown data
    burndown_data = []
    remaining_points = total_story_points
    
    # Group completions by date
    completions_by_date = {}
    for cp in completed_story_points:
        date_key = cp.completed_at.date()
        if date_key not in completions_by_date:
            completions_by_date[date_key] = 0
        completions_by_date[date_key] += cp.story_points
    
    # Calculate ideal burndown
    start_date = min(task.created_at.date() for task in tasks) if tasks else date.today()
    end_date = max(task.updated_at.date() for task in tasks) if tasks else date.today()
    total_days = (end_date - start_date).days + 1
    ideal_burn_rate = total_story_points / total_days if total_days > 0 else 0
    
    # Generate daily burndown
    current_date = start_date
    while current_date <= end_date:
        # Actual burndown
        if current_date in completions_by_date:
            remaining_points -= completions_by_date[current_date]
        
        # Ideal burndown
        days_passed = (current_date - start_date).days
        ideal_remaining = total_story_points - (ideal_burn_rate * days_passed)
        
        burndown_data.append({
            "date": current_date.isoformat(),
            "actual_remaining": max(0, remaining_points),
            "ideal_remaining": max(0, ideal_remaining),
            "completed_today": completions_by_date.get(current_date, 0)
        })
        
        current_date += timedelta(days=1)
    
    return {
        "project_id": project_id,
        "sprint_id": sprint_id,
        "project_name": project.name,
        "total_story_points": total_story_points,
        "burndown_data": burndown_data,
        "summary": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_days": total_days,
            "ideal_burn_rate": round(ideal_burn_rate, 2),
            "current_remaining": max(0, remaining_points)
        }
    }

@router.get("/export/time-logs")
def export_time_logs(
    format: str = Query("csv", description="Export format: csv, json"),
    project_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Export time logs data"""
    
    # Get accessible projects
    from app.api.v1.endpoints.reports import get_accessible_projects
    accessible_projects = get_accessible_projects(current_user, db)
    
    # Build query
    query = db.query(TimeLog).join(Task).join(Project).join(User).filter(
        Project.id.in_(accessible_projects)
    )
    
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(TimeLog.start_time >= start_datetime)
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(TimeLog.start_time <= end_datetime)
    
    time_logs = query.all()
    
    if format.lower() == "csv":
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Date", "User", "Project", "Task", "Duration (Hours)", 
            "Duration (Minutes)", "Type", "Description"
        ])
        
        # Write data
        for log in time_logs:
            writer.writerow([
                log.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                f"{log.user.first_name} {log.user.last_name}",
                log.task.project.name,
                log.task.title,
                round((log.duration_minutes or 0) / 60, 2),
                log.duration_minutes or 0,
                "Manual" if log.is_manual else "Timer",
                log.description or ""
            ])
        
        output.seek(0)
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=time_logs.csv"}
        )
    
    elif format.lower() == "json":
        # Generate JSON
        data = []
        for log in time_logs:
            data.append({
                "date": log.start_time.isoformat(),
                "user": f"{log.user.first_name} {log.user.last_name}",
                "project": log.task.project.name,
                "task": log.task.title,
                "duration_hours": round((log.duration_minutes or 0) / 60, 2),
                "duration_minutes": log.duration_minutes or 0,
                "type": "Manual" if log.is_manual else "Timer",
                "description": log.description or ""
            })
        
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=time_logs.json"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'csv' or 'json'")

@router.get("/workload-analysis")
def get_workload_analysis(
    period_days: int = Query(30, description="Analysis period in days"),
    team_id: Optional[int] = Query(None, description="Filter by team"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze team workload and capacity"""
    
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.TEAM_LEADER]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_days)
    
    # Get users to analyze
    users_query = db.query(User).filter(User.is_active)
    
    if team_id:
        users_query = users_query.join(Team.members).filter(Team.id == team_id)
    elif current_user.role == UserRole.TEAM_LEADER:
        # Only analyze team leader's teams
        users_query = users_query.join(Team.members).join(Team).filter(
            Team.team_leader_id == current_user.id
        )
    
    users = users_query.all()
    
    workload_analysis = []
    
    for user in users:
        # Get time logs for the period
        time_logs = db.query(TimeLog).filter(
            TimeLog.user_id == user.id,
            TimeLog.start_time >= start_date,
            TimeLog.start_time <= end_date
        ).all()
        
        total_hours = sum(log.duration_minutes or 0 for log in time_logs) / 60
        working_days = period_days * 5 / 7  # Assume 5-day work week
        avg_hours_per_day = total_hours / working_days if working_days > 0 else 0
        
        # Get active tasks
        active_tasks = db.query(Task).filter(
            Task.assignee_id == user.id,
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS])
        ).count()
        
        # Get story points in progress
        active_story_points = db.query(func.sum(Task.story_points)).filter(
            Task.assignee_id == user.id,
            Task.status.in_([TaskStatus.TODO, TaskStatus.IN_PROGRESS]),
            Task.story_points.isnot(None)
        ).scalar() or 0
        
        # Calculate workload level
        if avg_hours_per_day < 4:
            workload_level = "Low"
        elif avg_hours_per_day < 6:
            workload_level = "Normal"
        elif avg_hours_per_day < 8:
            workload_level = "High"
        else:
            workload_level = "Overloaded"
        
        workload_analysis.append({
            "user_name": f"{user.first_name} {user.last_name}",
            "user_role": user.role.value,
            "total_hours": round(total_hours, 2),
            "avg_hours_per_day": round(avg_hours_per_day, 2),
            "active_tasks": active_tasks,
            "active_story_points": int(active_story_points),
            "workload_level": workload_level,
            "utilization_percentage": round((avg_hours_per_day / 8) * 100, 1) if avg_hours_per_day <= 8 else 100
        })
    
    # Sort by workload level
    workload_order = {"Overloaded": 0, "High": 1, "Normal": 2, "Low": 3}
    workload_analysis.sort(key=lambda x: workload_order.get(x["workload_level"], 4))
    
    return {
        "analysis_period": {
            "start_date": start_date.date().isoformat(),
            "end_date": end_date.date().isoformat(),
            "days": period_days
        },
        "team_filter": team_id,
        "workload_analysis": workload_analysis,
        "summary": {
            "total_users": len(workload_analysis),
            "overloaded_users": len([u for u in workload_analysis if u["workload_level"] == "Overloaded"]),
            "avg_utilization": round(sum(u["utilization_percentage"] for u in workload_analysis) / len(workload_analysis), 1) if workload_analysis else 0
        }
    }
