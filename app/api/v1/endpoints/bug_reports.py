"""
Bug Report management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.bug_report import BugReport
from app.models.task import Task
from app.schemas.bug_report import BugReportCreate, BugReportUpdate, BugReportResponse

router = APIRouter()

@router.get("/", response_model=List[BugReportResponse])
def get_bug_reports(
    skip: int = 0,
    limit: int = 100,
    task_id: int = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all bug reports with optional filters"""
    query = db.query(BugReport)
    
    if task_id:
        query = query.filter(BugReport.task_id == task_id)
    if status:
        query = query.filter(BugReport.status == status)
    
    bug_reports = query.offset(skip).limit(limit).all()
    return bug_reports

@router.get("/{bug_report_id}", response_model=BugReportResponse)
def get_bug_report(
    bug_report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get bug report by ID"""
    bug_report = db.query(BugReport).filter(BugReport.id == bug_report_id).first()
    if not bug_report:
        raise HTTPException(status_code=404, detail="Bug report not found")
    return bug_report

@router.post("/", response_model=BugReportResponse)
def create_bug_report(
    bug_report: BugReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new bug report"""
    # Verify task exists if task_id is provided
    if bug_report.task_id:
        task = db.query(Task).filter(Task.id == bug_report.task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
    
    db_bug_report = BugReport(
        **bug_report.dict(),
        reported_by_id=current_user.id
    )
    db.add(db_bug_report)
    db.commit()
    db.refresh(db_bug_report)
    return db_bug_report

@router.put("/{bug_report_id}", response_model=BugReportResponse)
def update_bug_report(
    bug_report_id: int,
    bug_report_update: BugReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update bug report"""
    bug_report = db.query(BugReport).filter(BugReport.id == bug_report_id).first()
    if not bug_report:
        raise HTTPException(status_code=404, detail="Bug report not found")
    
    update_data = bug_report_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bug_report, field, value)
    
    db.commit()
    db.refresh(bug_report)
    return bug_report

@router.delete("/{bug_report_id}")
def delete_bug_report(
    bug_report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete bug report"""
    bug_report = db.query(BugReport).filter(BugReport.id == bug_report_id).first()
    if not bug_report:
        raise HTTPException(status_code=404, detail="Bug report not found")
    
    db.delete(bug_report)
    db.commit()
    return {"message": "Bug report deleted successfully"}

@router.post("/report-problem", response_model=BugReportResponse)
def report_problem(
    task_id: int,
    title: str,
    description: str,
    severity: str = "medium",
    priority: int = 5,
    steps_to_reproduce: str = "",
    expected_behavior: str = "",
    actual_behavior: str = "",
    add_to_backlog: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Report a problem with a specific task and optionally add to backlog"""
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create bug report
    bug_report = BugReport(
        title=title,
        description=description,
        severity=severity,
        steps_to_reproduce=steps_to_reproduce,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        task_id=task_id,
        reported_by_id=current_user.id
    )
    db.add(bug_report)
    
    # Optionally add to backlog
    if add_to_backlog:
        from app.models.backlog import Backlog
        backlog_item = Backlog(
            title=f"Fix: {title}",
            description=f"Bug Report #{bug_report.id}: {description}",
            project_id=task.project_id
        )
        db.add(backlog_item)
    
    db.commit()
    db.refresh(bug_report)
    return bug_report

@router.post("/report-general-problem", response_model=BugReportResponse)
def report_general_problem(
    project_id: int,
    title: str,
    description: str,
    task_id: int = None,
    severity: str = "medium",
    priority: int = 5,
    steps_to_reproduce: str = "",
    expected_behavior: str = "",
    actual_behavior: str = "",
    add_to_backlog: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Report a general problem and optionally add to backlog"""
    # Verify project exists
    from app.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Verify task exists if provided
    task = None
    if task_id:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
    
    # Create bug report
    bug_report = BugReport(
        title=title,
        description=description,
        severity=severity,
        steps_to_reproduce=steps_to_reproduce,
        expected_behavior=expected_behavior,
        actual_behavior=actual_behavior,
        task_id=task_id,
        reported_by_id=current_user.id
    )
    db.add(bug_report)
    
    # Optionally add to backlog
    if add_to_backlog:
        from app.models.backlog import Backlog
        backlog_item = Backlog(
            title=f"Fix: {title}",
            description=f"General Bug Report: {description}",
            project_id=project_id
        )
        db.add(backlog_item)
    
    db.commit()
    db.refresh(bug_report)
    return bug_report

@router.post("/report-simple-problem", response_model=BugReportResponse)
def report_simple_problem(
    project_id: int,
    title: str,
    description: str,
    severity: str = "medium",
    priority: int = 5,
    steps_to_reproduce: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Report a simple problem with minimal fields to a user-selected project"""
    # Verify project exists
    from app.models.project import Project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to this project
    has_access = False
    if current_user.role.value == 'admin':
        has_access = True
    elif current_user.role.value == 'project_manager':
        # Project managers can report bugs in any project
        has_access = True
    else:
        # Employees can report bugs in projects they have tasks in
        user_tasks_in_project = db.query(Task).filter(
            Task.project_id == project_id,
            Task.assignee_id == current_user.id
        ).first()
        has_access = user_tasks_in_project is not None
    
    if not has_access:
        raise HTTPException(status_code=403, detail="Not enough permissions for this project")
    
    # Create bug report
    bug_report = BugReport(
        title=title,
        description=description,
        severity=severity,
        steps_to_reproduce=steps_to_reproduce,
        task_id=None,  # Simple problems are not tied to specific tasks
        reported_by_id=current_user.id
    )
    
    db.add(bug_report)
    db.commit()
    db.refresh(bug_report)
    return bug_report
