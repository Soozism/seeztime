"""
Version schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VersionBase(BaseModel):
    version_number: str
    description: Optional[str] = None

class VersionCreate(VersionBase):
    project_id: int

class VersionUpdate(BaseModel):
    version_number: Optional[str] = None
    description: Optional[str] = None

class VersionResponse(VersionBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
