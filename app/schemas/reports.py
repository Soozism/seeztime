"""
Reporting schemas for analytics and insights
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date

class ReportFilters(BaseModel):
    project_id: Optional[int] = None
    user_id: Optional[int] = None
    team_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class TimeLogReport(BaseModel):
    date: datetime
    user_name: str
    project_name: str
    task_title: str
    duration_minutes: int
    duration_hours: float
    log_type: str  # "Manual" or "Timer"
    description: Optional[str] = None

class ProjectTimeStats(BaseModel):
    project_name: str
    total_minutes: int
    total_hours: float
    task_count: int
    user_count: int

class UserTimeStats(BaseModel):
    user_name: str
    total_minutes: int
    total_hours: float
    task_count: int
    project_count: int

class WeeklyTrendData(BaseModel):
    date: date
    hours: float
    minutes: int

class StoryPointsReport(BaseModel):
    user_name: str
    project_name: str
    task_title: str
    story_points: int
    completed_at: datetime

class UserStoryPerformance(BaseModel):
    user_name: str
    planned_points: int
    completed_points: int
    completion_rate: float
    active_tasks: int
    completed_tasks: int

class ProjectStoryStats(BaseModel):
    project_name: str
    total_points_planned: int
    total_points_completed: int
    completion_rate: float
    active_tasks: int
    completed_tasks: int

class TeamProductivityReport(BaseModel):
    team_name: str
    team_leader: str
    member_count: int
    total_hours: float
    total_story_points: int
    projects_count: int
    avg_completion_rate: float

class DashboardSummary(BaseModel):
    total_hours_logged: float
    total_story_points_completed: int
    active_projects: int
    active_tasks: int
    total_users: int
    total_teams: int

class TimeReportResponse(BaseModel):
    summary: Dict[str, Any]
    project_stats: List[ProjectTimeStats]
    user_stats: List[UserTimeStats]
    detailed_logs: List[TimeLogReport]
    weekly_trend: List[WeeklyTrendData]
    applied_filters: ReportFilters

class StoryPointsReportResponse(BaseModel):
    summary: Dict[str, Any]
    project_stats: List[ProjectStoryStats]
    user_performance: List[UserStoryPerformance]
    detailed_completions: List[StoryPointsReport]
    applied_filters: ReportFilters

class TeamReportResponse(BaseModel):
    summary: Dict[str, Any]
    team_productivity: List[TeamProductivityReport]
    applied_filters: ReportFilters

class DashboardReportResponse(BaseModel):
    dashboard_summary: DashboardSummary
    recent_activities: List[TimeLogReport]
    top_performers: List[UserStoryPerformance]
    project_progress: List[ProjectStoryStats]
