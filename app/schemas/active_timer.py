"""
Active Timer schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ActiveTimerBase(BaseModel):
    task_id: int

class ActiveTimerCreate(ActiveTimerBase):
    pass

class ActiveTimerResponse(ActiveTimerBase):
    id: int
    user_id: int
    start_time: datetime
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    task_title: Optional[str] = None
    task_description: Optional[str] = None
    project_name: Optional[str] = None
    elapsed_seconds: Optional[int] = None

    class Config:
        from_attributes = True

class TimerStartResponse(BaseModel):
    message: str
    timer_id: int
    task_id: int
    task_title: str
    start_time: datetime

class TimerStopResponse(BaseModel):
    message: str
    timer_id: int
    elapsed_hours: float
    elapsed_seconds: int
    time_log_id: int
