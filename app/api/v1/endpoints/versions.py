"""
Version management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.version import Version
from app.models.team import Team
from app.models.enums import UserRole
from app.schemas.version import VersionCreate, VersionUpdate, VersionResponse

router = APIRouter()

def check_team_project_access(user: User, project: Project, db: Session) -> bool:
    """Check if user has access to project through team membership"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    
    # Check if user is team leader of any team assigned to the project
    team_leader_access = db.query(Team).filter(
        Team.team_leader_id == user.id,
        Team.projects.any(Project.id == project.id)
    ).first()
    if team_leader_access:
        return True
    
    # Check if user is a member of any team assigned to the project
    member_access = db.query(Team).join(Team.members).filter(
        User.id == user.id,
        Team.projects.any(Project.id == project.id)
    ).first()
    if member_access:
        return True
    
    return False

@router.get("/project/{project_id}/versions", response_model=List[VersionResponse])
def get_project_versions(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all versions for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check project access
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    versions = db.query(Version).filter(Version.project_id == project_id).all()
    return versions

@router.post("/project/{project_id}/versions", response_model=VersionResponse)
def create_project_version(
    project_id: int,
    version: VersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new project version"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check project access
    if not check_team_project_access(current_user, project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if version number already exists for this project
    existing = db.query(Version).filter(
        Version.project_id == project_id,
        Version.version_number == version.version_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Version number already exists")
    
    db_version = Version(
        project_id=project_id,
        version_number=version.version_number,
        description=version.description
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return db_version

@router.get("/versions/{version_id}", response_model=VersionResponse)
def get_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific version"""
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Check project access
    if not check_team_project_access(current_user, version.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return version

@router.put("/versions/{version_id}", response_model=VersionResponse)
def update_version(
    version_id: int,
    version_update: VersionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a version"""
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Check project access
    if not check_team_project_access(current_user, version.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update version data
    for key, value in version_update.dict(exclude_unset=True).items():
        setattr(version, key, value)
    
    db.commit()
    db.refresh(version)
    return version

@router.delete("/versions/{version_id}")
def delete_version(
    version_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a version"""
    version = db.query(Version).filter(Version.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Check project access
    if not check_team_project_access(current_user, version.project, db):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(version)
    db.commit()
    return {"message": "Version deleted successfully"}
