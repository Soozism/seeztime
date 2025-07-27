"""
Bug Report schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import BugSeverity, BugStatus

class BugReportBase(BaseModel):
    title: str
    description: str
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    severity: BugSeverity = BugSeverity.MEDIUM
    status: BugStatus = BugStatus.OPEN

class BugReportCreate(BugReportBase):
    task_id: Optional[int] = None

class BugReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    severity: Optional[BugSeverity] = None
    status: Optional[BugStatus] = None

class BugReportResponse(BugReportBase):
    id: int
    task_id: Optional[int] = None
    reported_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
