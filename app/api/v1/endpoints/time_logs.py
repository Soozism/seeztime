"""
Time Log management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.time_log import TimeLog
from app.models.task import Task
from app.models.active_timer import ActiveTimer
from app.schemas.time_log import TimeLogCreate, TimeLogUpdate, TimeLogResponse
from app.schemas.active_timer import ActiveTimerResponse, TimerStartResponse, TimerStopResponse

router = APIRouter()

@router.get("/", response_model=List[TimeLogResponse])
def get_time_logs(
    skip: int = 0,
    limit: int = 100,
    task_id: int = None,
    user_id: int = None,
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all time logs with optional filters including time range"""
    query = db.query(TimeLog)
    
    if task_id:
        query = query.filter(TimeLog.task_id == task_id)
    if user_id:
        query = query.filter(TimeLog.user_id == user_id)
    
    # Add time filtering
    if start_date:
        query = query.filter(TimeLog.date >= start_date)
    if end_date:
        query = query.filter(TimeLog.date <= end_date)
    
    time_logs = query.offset(skip).limit(limit).all()
    return time_logs

@router.get("/active-timer", response_model=ActiveTimerResponse)
def get_active_timer(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's active timer if any"""
    from datetime import datetime
    from sqlalchemy.orm import joinedload
    
    active_timer = db.query(ActiveTimer).options(
        joinedload(ActiveTimer.task).joinedload(Task.project)
    ).filter(
        ActiveTimer.user_id == current_user.id,
        ActiveTimer.is_active.is_(True)
    ).first()
    
    if not active_timer:
        raise HTTPException(status_code=404, detail="No active timer found")
    
    # Calculate elapsed seconds
    elapsed_seconds = int((datetime.utcnow() - active_timer.start_time).total_seconds())
    
    response_data = {
        "id": active_timer.id,
        "task_id": active_timer.task_id,
        "user_id": active_timer.user_id,
        "start_time": active_timer.start_time,
        "is_active": active_timer.is_active,
        "created_at": active_timer.created_at,
        "updated_at": active_timer.updated_at,
        "task_title": active_timer.task.title,
        "task_description": active_timer.task.description,
        "project_name": active_timer.task.project.name,
        "elapsed_seconds": elapsed_seconds
    }
    
    return ActiveTimerResponse(**response_data)

@router.get("/{time_log_id}", response_model=TimeLogResponse)
def get_time_log(
    time_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time log by ID"""
    time_log = db.query(TimeLog).filter(TimeLog.id == time_log_id).first()
    if not time_log:
        raise HTTPException(status_code=404, detail="Time log not found")
    return time_log

@router.post("/", response_model=TimeLogResponse)
def create_time_log(
    time_log: TimeLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new time log entry"""
    # Verify task exists
    task = db.query(Task).filter(Task.id == time_log.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_time_log = TimeLog(
        **time_log.dict(),
        user_id=current_user.id
    )
    db.add(db_time_log)
    
    # Update task actual hours
    task.actual_hours = (task.actual_hours or 0) + time_log.hours
    
    db.commit()
    db.refresh(db_time_log)
    return db_time_log

@router.put("/{time_log_id}", response_model=TimeLogResponse)
def update_time_log(
    time_log_id: int,
    time_log_update: TimeLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update time log entry"""
    time_log = db.query(TimeLog).filter(TimeLog.id == time_log_id).first()
    if not time_log:
        raise HTTPException(status_code=404, detail="Time log not found")
    
    # Only allow users to update their own time logs
    if time_log.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    old_hours = time_log.hours
    update_data = time_log_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(time_log, field, value)
    
    # Update task actual hours if hours changed
    if 'hours' in update_data:
        task = db.query(Task).filter(Task.id == time_log.task_id).first()
        task.actual_hours = (task.actual_hours or 0) - old_hours + time_log.hours
    
    db.commit()
    db.refresh(time_log)
    return time_log

@router.delete("/{time_log_id}")
def delete_time_log(
    time_log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete time log entry"""
    time_log = db.query(TimeLog).filter(TimeLog.id == time_log_id).first()
    if not time_log:
        raise HTTPException(status_code=404, detail="Time log not found")
    
    # Only allow users to delete their own time logs
    if time_log.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update task actual hours
    task = db.query(Task).filter(Task.id == time_log.task_id).first()
    task.actual_hours = (task.actual_hours or 0) - time_log.hours
    
    db.delete(time_log)
    db.commit()
    return {"message": "Time log deleted successfully"}

@router.get("/task/{task_id}", response_model=List[TimeLogResponse])
def get_task_time_logs(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all time logs for a specific task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    time_logs = db.query(TimeLog).filter(TimeLog.task_id == task_id).all()
    return time_logs

@router.post("/log-time", response_model=TimeLogResponse)
def log_time(
    task_id: int,
    duration_minutes: int,
    description: str = "",
    is_manual: bool = True,
    log_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Log time for a task with enhanced parameters"""
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions
    if current_user.role.value == 'developer' and task.assignee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check for duplicate submissions (same user, task, duration within last 10 seconds)
    from datetime import datetime, timedelta
    recent_cutoff = datetime.utcnow() - timedelta(seconds=10)
    recent_duplicate = db.query(TimeLog).filter(
        TimeLog.task_id == task_id,
        TimeLog.user_id == current_user.id,
        TimeLog.hours == duration_minutes / 60.0  # Convert to hours
    ).filter(TimeLog.created_at > recent_cutoff).first()
    
    if recent_duplicate:
        raise HTTPException(status_code=409, detail="Duplicate time log detected")
    
    # Parse date if provided
    log_datetime = datetime.utcnow()
    if log_date:
        try:
            log_datetime = datetime.fromisoformat(log_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Convert minutes to hours
    hours = duration_minutes / 60.0
    
    time_log = TimeLog(
        task_id=task_id,
        user_id=current_user.id,
        date=log_datetime,
        hours=hours,
        description=description
    )
    
    db.add(time_log)
    
    # Update task actual hours
    task.actual_hours = (task.actual_hours or 0) + hours
    
    db.commit()
    db.refresh(time_log)
    return time_log

@router.post("/start-timer", response_model=TimerStartResponse)
def start_timer(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Start a live timer for a task"""
    # Check if there's already an active timer for this user
    active_timer = db.query(ActiveTimer).filter(
        ActiveTimer.user_id == current_user.id,
        ActiveTimer.is_active.is_(True)
    ).first()
    
    if active_timer:
        raise HTTPException(
            status_code=409, 
            detail=f"You already have an active timer running for task {active_timer.task_id}"
        )
    
    # Verify task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check permissions - user must be assigned to the task or have admin/manager role
    if (current_user.role.value not in ['admin', 'project_manager'] and 
        task.assignee_id != current_user.id):
        raise HTTPException(
            status_code=403, 
            detail="You can only start timers for tasks assigned to you"
        )
    
    from datetime import datetime
    new_timer = ActiveTimer(
        task_id=task_id,
        user_id=current_user.id,
        start_time=datetime.utcnow(),
        is_active=True
    )
    
    db.add(new_timer)
    db.commit()
    db.refresh(new_timer)
    
    return TimerStartResponse(
        message="Timer started successfully",
        timer_id=new_timer.id,
        task_id=task_id,
        task_title=task.title,
        start_time=new_timer.start_time
    )

@router.post("/stop-timer", response_model=TimerStopResponse)
def stop_timer(
    timer_id: int = None,
    description: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Stop an active timer and create a time log entry"""
    # Find active timer
    if timer_id:
        active_timer = db.query(ActiveTimer).filter(
            ActiveTimer.id == timer_id,
            ActiveTimer.user_id == current_user.id,
            ActiveTimer.is_active.is_(True)
        ).first()
    else:
        # Find any active timer for this user
        active_timer = db.query(ActiveTimer).filter(
            ActiveTimer.user_id == current_user.id,
            ActiveTimer.is_active.is_(True)
        ).first()
    
    if not active_timer:
        raise HTTPException(status_code=404, detail="No active timer found")
    
    # Calculate elapsed time
    from datetime import datetime
    end_time = datetime.utcnow()
    elapsed_seconds = int((end_time - active_timer.start_time).total_seconds())
    elapsed_hours = elapsed_seconds / 3600
    
    # Create time log entry
    time_log = TimeLog(
        task_id=active_timer.task_id,
        user_id=current_user.id,
        date=active_timer.start_time,
        hours=elapsed_hours,
        description=description or f"Live timer session: {elapsed_hours:.2f} hours"
    )
    
    db.add(time_log)
    
    # Update task actual hours
    task = db.query(Task).filter(Task.id == active_timer.task_id).first()
    task.actual_hours = (task.actual_hours or 0) + elapsed_hours
    
    # Mark timer as inactive
    active_timer.is_active = False
    
    db.commit()
    db.refresh(time_log)
    
    return TimerStopResponse(
        message="Timer stopped and time logged successfully",
        timer_id=active_timer.id,
        elapsed_hours=round(elapsed_hours, 2),
        elapsed_seconds=elapsed_seconds,
        time_log_id=time_log.id
    )

@router.get("/user/me", response_model=List[TimeLogResponse])
def get_my_time_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's time logs"""
    time_logs = db.query(TimeLog).filter(TimeLog.user_id == current_user.id).offset(skip).limit(limit).all()
    return time_logs
