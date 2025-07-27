"""
Backlog schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BacklogBase(BaseModel):
    title: str
    description: Optional[str] = None

class BacklogCreate(BacklogBase):
    project_id: int

class BacklogUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class BacklogResponse(BacklogBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
