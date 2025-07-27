"""
Team schemas for request/response validation
"""

from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.schemas.user import UserResponse
from app.schemas.project import ProjectSimple

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    team_leader_id: int
    member_ids: Optional[List[int]] = []
    project_ids: Optional[List[int]] = []  # Projects to assign team to

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    team_leader_id: Optional[int] = None
    member_ids: Optional[List[int]] = None  # Complete list of member IDs to set
    add_member_ids: Optional[List[int]] = None  # Member IDs to add
    remove_member_ids: Optional[List[int]] = None  # Member IDs to remove
    project_ids: Optional[List[int]] = None  # Complete list of project IDs to set
    add_project_ids: Optional[List[int]] = None  # Project IDs to add
    remove_project_ids: Optional[List[int]] = None  # Project IDs to remove

class TeamMemberAdd(BaseModel):
    user_ids: List[int]

class TeamProjectAssign(BaseModel):
    project_ids: List[int]

class TeamResponse(TeamBase):
    id: int
    team_leader_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    team_leader: Optional[UserResponse] = None
    members: Optional[List[UserResponse]] = []
    projects: Optional[List[ProjectSimple]] = []
    project_count: Optional[int] = 0

    class Config:
        from_attributes = True
