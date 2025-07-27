"""
API v1 router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, projects, phases, tasks, sprints, backlogs, bug_reports, time_logs, 
    dashboard, milestones, teams, reports, advanced_reports, task_dependencies, 
    versions, tags, advanced_queries
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(phases.router, prefix="/phases", tags=["phases"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
api_router.include_router(backlogs.router, prefix="/backlogs", tags=["backlogs"])
api_router.include_router(bug_reports.router, prefix="/bug-reports", tags=["bug-reports"])
api_router.include_router(time_logs.router, prefix="/time-logs", tags=["time-logs"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(advanced_reports.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(task_dependencies.router, prefix="/dependencies", tags=["task-dependencies"])
api_router.include_router(versions.router, prefix="/versions", tags=["versions"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(advanced_queries.router, prefix="/queries", tags=["advanced-queries"])
