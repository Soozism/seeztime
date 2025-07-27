"""
Time Log schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TimeLogBase(BaseModel):
    description: Optional[str] = None
    hours: float
    date: datetime

class TimeLogCreate(TimeLogBase):
    task_id: int

class TimeLogUpdate(BaseModel):
    description: Optional[str] = None
    hours: Optional[float] = None
    date: Optional[datetime] = None

class TimeLogResponse(TimeLogBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
