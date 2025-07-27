"""
Comprehensive reporting endpoints for analytics and insights
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, date, timedelta

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.team import Team
from app.models.time_log import TimeLog
from app.models.completed_sp import CompletedStoryPoints
from app.models.enums import UserRole, TaskStatus
from app.schemas.reports import (
    ReportFilters, TimeReportResponse, StoryPointsReportResponse, 
    TeamReportResponse, DashboardReportResponse, TimeLogReport, 
    ProjectTimeStats, UserTimeStats, WeeklyTrendData, StoryPointsReport,
    UserStoryPerformance, ProjectStoryStats, TeamProductivityReport,
    DashboardSummary
)

router = APIRouter()

def get_accessible_projects(user: User, db: Session) -> List[int]:
    """Get list of project IDs accessible by the user"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return [p.id for p in db.query(Project).all()]
    elif user.role == UserRole.TEAM_LEADER:
        # Get projects assigned to teams led by this user
        teams = db.query(Team).filter(Team.team_leader_id == user.id).all()
        project_ids = []
        for team in teams:
            project_ids.extend([p.id for p in team.projects])
        return list(set(project_ids))
    else:
        # Regular users - only projects where they're team members
        teams = db.query(Team).join(Team.members).filter(User.id == user.id).all()
        project_ids = []
        for team in teams:
            project_ids.extend([p.id for p in team.projects])
        return list(set(project_ids))

def apply_report_filters(query, filters: ReportFilters, time_log_alias=None):
    """Apply common filters to queries"""
    if filters.project_id:
        if time_log_alias:
            # For time log queries, filter through task
            query = query.join(Task).filter(Task.project_id == filters.project_id)
        else:
            query = query.filter(Project.id == filters.project_id)
    
    if filters.user_id:
        query = query.filter(User.id == filters.user_id)
    
    if filters.start_date:
        start_datetime = datetime.combine(filters.start_date, datetime.min.time())
        if time_log_alias:
            query = query.filter(TimeLog.start_time >= start_datetime)
        else:
            query = query.filter(Task.created_at >= start_datetime)
    
    if filters.end_date:
        end_datetime = datetime.combine(filters.end_date, datetime.max.time())
        if time_log_alias:
            query = query.filter(TimeLog.start_time <= end_datetime)
        else:
            query = query.filter(Task.created_at <= end_datetime)
    
    return query

@router.get("/time-logs", response_model=TimeReportResponse)
def get_time_report(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    start_date: Optional[date] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    include_details: bool = Query(True, description="Include detailed time logs"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comprehensive time tracking report"""
    filters = ReportFilters(
        project_id=project_id,
        user_id=user_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get accessible projects for permission filtering
    accessible_projects = get_accessible_projects(current_user, db)
    
    # Base query for time logs
    time_logs_query = db.query(TimeLog).join(Task).join(Project).join(User)
    
    # Apply permission filtering
    time_logs_query = time_logs_query.filter(Project.id.in_(accessible_projects))
    
    # Apply filters
    if filters.project_id:
        time_logs_query = time_logs_query.filter(Task.project_id == filters.project_id)
    if filters.user_id:
        time_logs_query = time_logs_query.filter(TimeLog.user_id == filters.user_id)
    if filters.team_id:
        # Filter by team members
        team_user_ids = db.query(User.id).join(Team.members).filter(Team.id == filters.team_id).subquery()
        time_logs_query = time_logs_query.filter(TimeLog.user_id.in_(team_user_ids))
    if filters.start_date:
        start_datetime = datetime.combine(filters.start_date, datetime.min.time())
        time_logs_query = time_logs_query.filter(TimeLog.start_time >= start_datetime)
    if filters.end_date:
        end_datetime = datetime.combine(filters.end_date, datetime.max.time())
        time_logs_query = time_logs_query.filter(TimeLog.start_time <= end_datetime)
    
    time_logs = time_logs_query.options(
        joinedload(TimeLog.user),
        joinedload(TimeLog.task).joinedload(Task.project)
    ).all()
    
    # Calculate summary stats
    total_minutes = sum(log.duration_minutes or 0 for log in time_logs)
    total_hours = round(total_minutes / 60, 2)
    
    # Project time stats
    project_stats = {}
    for log in time_logs:
        project_name = log.task.project.name
        if project_name not in project_stats:
            project_stats[project_name] = {
                'total_minutes': 0,
                'users': set(),
                'tasks': set()
            }
        project_stats[project_name]['total_minutes'] += log.duration_minutes or 0
        project_stats[project_name]['users'].add(log.user.id)
        project_stats[project_name]['tasks'].add(log.task.id)
    
    project_time_stats = [
        ProjectTimeStats(
            project_name=name,
            total_minutes=stats['total_minutes'],
            total_hours=round(stats['total_minutes'] / 60, 2),
            task_count=len(stats['tasks']),
            user_count=len(stats['users'])
        )
        for name, stats in project_stats.items()
    ]
    
    # User time stats
    user_stats = {}
    for log in time_logs:
        user_name = f"{log.user.first_name} {log.user.last_name}"
        if user_name not in user_stats:
            user_stats[user_name] = {
                'total_minutes': 0,
                'projects': set(),
                'tasks': set()
            }
        user_stats[user_name]['total_minutes'] += log.duration_minutes or 0
        user_stats[user_name]['projects'].add(log.task.project.id)
        user_stats[user_name]['tasks'].add(log.task.id)
    
    user_time_stats = [
        UserTimeStats(
            user_name=name,
            total_minutes=stats['total_minutes'],
            total_hours=round(stats['total_minutes'] / 60, 2),
            task_count=len(stats['tasks']),
            project_count=len(stats['projects'])
        )
        for name, stats in user_stats.items()
    ]
    
    # Weekly trend (last 7 days)
    weekly_data = []
    today = date.today()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_minutes = sum(
            log.duration_minutes or 0 
            for log in time_logs 
            if log.start_time.date() == day
        )
        weekly_data.append(WeeklyTrendData(
            date=day,
            hours=round(day_minutes / 60, 1),
            minutes=day_minutes
        ))
    
    # Detailed logs
    detailed_logs = []
    if include_details:
        for log in time_logs[-100:]:  # Last 100 entries
            detailed_logs.append(TimeLogReport(
                date=log.start_time,
                user_name=f"{log.user.first_name} {log.user.last_name}",
                project_name=log.task.project.name,
                task_title=log.task.title,
                duration_minutes=log.duration_minutes or 0,
                duration_hours=round((log.duration_minutes or 0) / 60, 2),
                log_type="Manual" if log.is_manual else "Timer",
                description=log.description
            ))
    
    return TimeReportResponse(
        summary={
            "total_hours": total_hours,
            "total_minutes": total_minutes,
            "entries_count": len(time_logs),
            "projects_count": len(project_stats),
            "users_count": len(user_stats)
        },
        project_stats=project_time_stats,
        user_stats=user_time_stats,
        detailed_logs=detailed_logs,
        weekly_trend=weekly_data,
        applied_filters=filters
    )

@router.get("/story-points", response_model=StoryPointsReportResponse)
def get_story_points_report(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    team_id: Optional[int] = Query(None, description="Filter by team ID"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get story points completion report"""
    filters = ReportFilters(
        project_id=project_id,
        user_id=user_id,
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get accessible projects
    accessible_projects = get_accessible_projects(current_user, db)
    
    # Get completed story points
    completed_query = db.query(CompletedStoryPoints).join(Project).join(User)
    completed_query = completed_query.filter(Project.id.in_(accessible_projects))
    
    # Apply filters
    if filters.project_id:
        completed_query = completed_query.filter(CompletedStoryPoints.project_id == filters.project_id)
    if filters.user_id:
        completed_query = completed_query.filter(CompletedStoryPoints.user_id == filters.user_id)
    if filters.team_id:
        team_user_ids = db.query(User.id).join(Team.members).filter(Team.id == filters.team_id).subquery()
        completed_query = completed_query.filter(CompletedStoryPoints.user_id.in_(team_user_ids))
    if filters.start_date:
        start_datetime = datetime.combine(filters.start_date, datetime.min.time())
        completed_query = completed_query.filter(CompletedStoryPoints.completed_at >= start_datetime)
    if filters.end_date:
        end_datetime = datetime.combine(filters.end_date, datetime.max.time())
        completed_query = completed_query.filter(CompletedStoryPoints.completed_at <= end_datetime)
    
    completed_points = completed_query.options(
        joinedload(CompletedStoryPoints.project),
        joinedload(CompletedStoryPoints.user),
        joinedload(CompletedStoryPoints.task)
    ).all()
    
    # Calculate project stats
    project_stats = {}
    for cp in completed_points:
        project_name = cp.project.name
        if project_name not in project_stats:
            project_stats[project_name] = {
                'completed_points': 0,
                'completed_tasks': 0,
                'total_planned': 0,
                'active_tasks': 0
            }
        project_stats[project_name]['completed_points'] += cp.story_points
        project_stats[project_name]['completed_tasks'] += 1
    
    # Get planned points for each project
    for project_name in project_stats.keys():
        project = db.query(Project).filter(Project.name == project_name).first()
        if project:
            # Get all tasks in project with story points
            tasks = db.query(Task).filter(
                Task.project_id == project.id,
                Task.story_points.isnot(None)
            ).all()
            
            project_stats[project_name]['total_planned'] = sum(t.story_points for t in tasks)
            project_stats[project_name]['active_tasks'] = len([t for t in tasks if t.status != TaskStatus.DONE])
    
    project_story_stats = [
        ProjectStoryStats(
            project_name=name,
            total_points_planned=stats['total_planned'],
            total_points_completed=stats['completed_points'],
            completion_rate=round((stats['completed_points'] / stats['total_planned'] * 100) if stats['total_planned'] > 0 else 0, 1),
            active_tasks=stats['active_tasks'],
            completed_tasks=stats['completed_tasks']
        )
        for name, stats in project_stats.items()
    ]
    
    # Calculate user performance
    user_performance = {}
    for cp in completed_points:
        user_name = f"{cp.user.first_name} {cp.user.last_name}"
        if user_name not in user_performance:
            user_performance[user_name] = {
                'completed_points': 0,
                'completed_tasks': 0,
                'planned_points': 0,
                'active_tasks': 0
            }
        user_performance[user_name]['completed_points'] += cp.story_points
        user_performance[user_name]['completed_tasks'] += 1
    
    # Get planned points for each user
    for user_name in user_performance.keys():
        user = db.query(User).filter(
            func.concat(User.first_name, ' ', User.last_name) == user_name
        ).first()
        if user:
            tasks = db.query(Task).filter(
                Task.assignee_id == user.id,
                Task.story_points.isnot(None),
                Task.project_id.in_(accessible_projects)
            ).all()
            
            user_performance[user_name]['planned_points'] = sum(t.story_points for t in tasks)
            user_performance[user_name]['active_tasks'] = len([t for t in tasks if t.status != TaskStatus.DONE])
    
    user_story_performance = [
        UserStoryPerformance(
            user_name=name,
            planned_points=stats['planned_points'],
            completed_points=stats['completed_points'],
            completion_rate=round((stats['completed_points'] / stats['planned_points'] * 100) if stats['planned_points'] > 0 else 0, 1),
            active_tasks=stats['active_tasks'],
            completed_tasks=stats['completed_tasks']
        )
        for name, stats in user_performance.items()
    ]
    
    # Detailed completions
    detailed_completions = [
        StoryPointsReport(
            user_name=f"{cp.user.first_name} {cp.user.last_name}",
            project_name=cp.project.name,
            task_title=cp.task.title if cp.task else "Unknown Task",
            story_points=cp.story_points,
            completed_at=cp.completed_at
        )
        for cp in completed_points[-50:]  # Last 50 entries
    ]
    
    total_completed = sum(cp.story_points for cp in completed_points)
    
    return StoryPointsReportResponse(
        summary={
            "total_story_points_completed": total_completed,
            "completions_count": len(completed_points),
            "projects_count": len(project_stats),
            "users_count": len(user_performance)
        },
        project_stats=project_story_stats,
        user_performance=user_story_performance,
        detailed_completions=detailed_completions,
        applied_filters=filters
    )

@router.get("/teams", response_model=TeamReportResponse)
def get_team_report(
    team_id: Optional[int] = Query(None, description="Filter by specific team"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    start_date: Optional[date] = Query(None, description="Filter from date"),
    end_date: Optional[date] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get team productivity report"""
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER, UserRole.TEAM_LEADER]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    filters = ReportFilters(
        team_id=team_id,
        project_id=project_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get teams based on user role
    teams_query = db.query(Team)
    if current_user.role == UserRole.TEAM_LEADER:
        teams_query = teams_query.filter(Team.team_leader_id == current_user.id)
    
    if filters.team_id:
        teams_query = teams_query.filter(Team.id == filters.team_id)
    
    teams = teams_query.options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).all()
    
    team_productivity = []
    for team in teams:
        # Calculate team metrics
        team_member_ids = [m.id for m in team.members]
        
        # Get time logs for team members
        time_logs_query = db.query(TimeLog).filter(TimeLog.user_id.in_(team_member_ids))
        
        if filters.project_id:
            time_logs_query = time_logs_query.join(Task).filter(Task.project_id == filters.project_id)
        if filters.start_date:
            start_datetime = datetime.combine(filters.start_date, datetime.min.time())
            time_logs_query = time_logs_query.filter(TimeLog.start_time >= start_datetime)
        if filters.end_date:
            end_datetime = datetime.combine(filters.end_date, datetime.max.time())
            time_logs_query = time_logs_query.filter(TimeLog.start_time <= end_datetime)
        
        team_time_logs = time_logs_query.all()
        total_hours = sum(log.duration_minutes or 0 for log in team_time_logs) / 60
        
        # Get story points for team
        story_points_query = db.query(CompletedStoryPoints).filter(
            CompletedStoryPoints.user_id.in_(team_member_ids)
        )
        
        if filters.project_id:
            story_points_query = story_points_query.filter(CompletedStoryPoints.project_id == filters.project_id)
        if filters.start_date:
            start_datetime = datetime.combine(filters.start_date, datetime.min.time())
            story_points_query = story_points_query.filter(CompletedStoryPoints.completed_at >= start_datetime)
        if filters.end_date:
            end_datetime = datetime.combine(filters.end_date, datetime.max.time())
            story_points_query = story_points_query.filter(CompletedStoryPoints.completed_at <= end_datetime)
        
        team_story_points = story_points_query.all()
        total_story_points = sum(sp.story_points for sp in team_story_points)
        
        # Calculate average completion rate
        completed_tasks = len(team_story_points)
        total_tasks = db.query(Task).filter(
            Task.assignee_id.in_(team_member_ids),
            Task.story_points.isnot(None)
        ).count()
        
        avg_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        team_productivity.append(TeamProductivityReport(
            team_name=team.name,
            team_leader=f"{team.team_leader.first_name} {team.team_leader.last_name}",
            member_count=len(team.members),
            total_hours=round(total_hours, 2),
            total_story_points=total_story_points,
            projects_count=len(team.projects),
            avg_completion_rate=round(avg_completion_rate, 1)
        ))
    
    return TeamReportResponse(
        summary={
            "teams_count": len(teams),
            "total_members": sum(len(team.members) for team in teams),
            "total_projects": len(set(p.id for team in teams for p in team.projects))
        },
        team_productivity=team_productivity,
        applied_filters=filters
    )

@router.get("/dashboard", response_model=DashboardReportResponse)
def get_dashboard_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get dashboard summary report"""
    accessible_projects = get_accessible_projects(current_user, db)
    
    # Dashboard summary
    total_hours = db.query(func.sum(TimeLog.duration_minutes)).join(Task).filter(
        Task.project_id.in_(accessible_projects)
    ).scalar() or 0
    total_hours = round(total_hours / 60, 2)
    
    total_story_points = db.query(func.sum(CompletedStoryPoints.story_points)).filter(
        CompletedStoryPoints.project_id.in_(accessible_projects)
    ).scalar() or 0
    
    active_projects = len(accessible_projects)
    active_tasks = db.query(Task).filter(
        Task.project_id.in_(accessible_projects),
        Task.status != TaskStatus.DONE
    ).count()
    
    total_users = db.query(User).filter(User.is_active).count()
    total_teams = db.query(Team).count()
    
    dashboard_summary = DashboardSummary(
        total_hours_logged=total_hours,
        total_story_points_completed=total_story_points,
        active_projects=active_projects,
        active_tasks=active_tasks,
        total_users=total_users,
        total_teams=total_teams
    )
    
    # Recent activities (last 10 time logs)
    recent_logs = db.query(TimeLog).join(Task).join(Project).join(User).filter(
        Project.id.in_(accessible_projects)
    ).order_by(TimeLog.start_time.desc()).limit(10).options(
        joinedload(TimeLog.user),
        joinedload(TimeLog.task).joinedload(Task.project)
    ).all()
    
    recent_activities = [
        TimeLogReport(
            date=log.start_time,
            user_name=f"{log.user.first_name} {log.user.last_name}",
            project_name=log.task.project.name,
            task_title=log.task.title,
            duration_minutes=log.duration_minutes or 0,
            duration_hours=round((log.duration_minutes or 0) / 60, 2),
            log_type="Manual" if log.is_manual else "Timer",
            description=log.description
        )
        for log in recent_logs
    ]
    
    # Top performers (by completed story points in last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    top_performers_data = db.query(
        User,
        func.sum(CompletedStoryPoints.story_points).label('total_points'),
        func.count(CompletedStoryPoints.id).label('completed_tasks')
    ).join(CompletedStoryPoints).filter(
        CompletedStoryPoints.project_id.in_(accessible_projects),
        CompletedStoryPoints.completed_at >= thirty_days_ago
    ).group_by(User.id).order_by(func.sum(CompletedStoryPoints.story_points).desc()).limit(5).all()
    
    top_performers = [
        UserStoryPerformance(
            user_name=f"{user.first_name} {user.last_name}",
            planned_points=0,  # Would need additional query
            completed_points=int(total_points),
            completion_rate=100.0,  # Simplified for dashboard
            active_tasks=0,  # Would need additional query
            completed_tasks=int(completed_tasks)
        )
        for user, total_points, completed_tasks in top_performers_data
    ]
    
    # Project progress
    project_progress = []
    for project_id in accessible_projects[:10]:  # Top 10 projects
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            total_tasks = db.query(Task).filter(Task.project_id == project_id).count()
            completed_tasks = db.query(Task).filter(
                Task.project_id == project_id,
                Task.status == TaskStatus.DONE
            ).count()
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            project_progress.append(ProjectStoryStats(
                project_name=project.name,
                total_points_planned=0,  # Simplified
                total_points_completed=0,  # Simplified
                completion_rate=round(completion_rate, 1),
                active_tasks=total_tasks - completed_tasks,
                completed_tasks=completed_tasks
            ))
    
    return DashboardReportResponse(
        dashboard_summary=dashboard_summary,
        recent_activities=recent_activities,
        top_performers=top_performers,
        project_progress=project_progress
    )
