"""
Team management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.team import Team
from app.models.project import Project
from app.models.enums import UserRole
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamMemberAdd, TeamProjectAssign

router = APIRouter()

def check_team_management_permission(current_user: User, team: Team = None):
    """Check if user has permission to manage teams"""
    if current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    if team and current_user.id == team.team_leader_id:
        return True
    return False

def check_project_assignment_permission(current_user: User):
    """Check if user can assign teams to projects"""
    return current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]

@router.get("/", response_model=List[TeamResponse])
def get_teams(
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[int] = None,
    include_members: bool = False,
    include_projects: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all teams with optional filters"""
    query = db.query(Team)
    
    # Add joinedload options based on parameters
    options = []
    if include_members:
        options.extend([joinedload(Team.team_leader), joinedload(Team.members)])
    if include_projects:
        options.append(joinedload(Team.projects))
    
    if options:
        query = query.options(*options)
    
    # Filter by project if specified
    if project_id:
        query = query.join(Team.projects).filter(Project.id == project_id)
    
    # Role-based filtering
    if current_user.role == UserRole.TEAM_LEADER:
        # Team leaders can only see their own teams
        query = query.filter(Team.team_leader_id == current_user.id)
    elif current_user.role in [UserRole.DEVELOPER, UserRole.TESTER, UserRole.VIEWER]:
        # Other roles can only see teams they're members of
        query = query.join(Team.members).filter(User.id == current_user.id)
    
    teams = query.offset(skip).limit(limit).all()
    
    # Add project count for each team
    for team in teams:
        team.project_count = len(team.projects)
    
    return teams

@router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new team with optional project assignment (Admin/Project Manager only)"""
    if not check_project_assignment_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and project managers can create teams"
        )
    
    # Verify team leader exists and has appropriate role
    team_leader = db.query(User).filter(User.id == team_data.team_leader_id).first()
    if not team_leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team leader not found"
        )
    
    if team_leader.role not in [UserRole.TEAM_LEADER, UserRole.PROJECT_MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team leader must have team_leader, project_manager, or admin role"
        )
    
    # Create team
    team = Team(
        name=team_data.name,
        description=team_data.description,
        team_leader_id=team_data.team_leader_id
    )
    
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # Add initial members if provided
    if team_data.member_ids:
        members = db.query(User).filter(User.id.in_(team_data.member_ids)).all()
        if len(members) != len(team_data.member_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more members not found"
            )
        team.members.extend(members)
    
    # Add team to projects if provided
    if team_data.project_ids:
        projects = db.query(Project).filter(Project.id.in_(team_data.project_ids)).all()
        if len(projects) != len(team_data.project_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more projects not found"
            )
        team.projects.extend(projects)
    
    db.commit()
    db.refresh(team)
    
    # Reload with all relationships for response
    team = db.query(Team).options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).filter(Team.id == team.id).first()
    
    # Add project count for response
    team.project_count = len(team.projects)
    return team

@router.get("/{team_id}", response_model=TeamResponse)
def get_team(
    team_id: int,
    include_members: bool = True,
    include_projects: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get team by ID"""
    query = db.query(Team).filter(Team.id == team_id)
    
    # Add joinedload options based on parameters
    options = []
    if include_members:
        options.extend([joinedload(Team.team_leader), joinedload(Team.members)])
    if include_projects:
        options.append(joinedload(Team.projects))
    
    if options:
        query = query.options(*options)
    
    team = query.first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Check permissions
    if current_user.role in [UserRole.DEVELOPER, UserRole.TESTER, UserRole.VIEWER]:
        # Check if user is a member of the team
        if current_user not in team.members and current_user.id != team.team_leader_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    team.project_count = len(team.projects)
    return team

@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update team including members and projects"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not check_team_management_permission(current_user, team):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update basic fields
    if team_data.name is not None:
        team.name = team_data.name
    if team_data.description is not None:
        team.description = team_data.description
    if team_data.team_leader_id is not None:
        # Verify new team leader exists
        new_leader = db.query(User).filter(User.id == team_data.team_leader_id).first()
        if not new_leader:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New team leader not found"
            )
        team.team_leader_id = team_data.team_leader_id
    
    # Handle member updates
    if team_data.member_ids is not None:
        # Complete replacement of members
        new_members = db.query(User).filter(User.id.in_(team_data.member_ids)).all()
        if len(new_members) != len(team_data.member_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more members not found"
            )
        # Ensure team leader is included in members
        leader_in_members = any(member.id == team.team_leader_id for member in new_members)
        if not leader_in_members:
            team_leader = db.query(User).filter(User.id == team.team_leader_id).first()
            if team_leader:
                new_members.append(team_leader)
        team.members = new_members
    
    # Handle adding specific members
    if team_data.add_member_ids:
        users_to_add = db.query(User).filter(User.id.in_(team_data.add_member_ids)).all()
        if len(users_to_add) != len(team_data.add_member_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more users to add not found"
            )
        # Add users to team (avoiding duplicates)
        current_member_ids = {member.id for member in team.members}
        for user in users_to_add:
            if user.id not in current_member_ids:
                team.members.append(user)
    
    # Handle removing specific members
    if team_data.remove_member_ids:
        for user_id in team_data.remove_member_ids:
            # Cannot remove team leader
            if user_id == team.team_leader_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot remove team leader (user {user_id}) from team"
                )
            # Find and remove user
            user_to_remove = None
            for member in team.members:
                if member.id == user_id:
                    user_to_remove = member
                    break
            if user_to_remove:
                team.members.remove(user_to_remove)
    
    # Handle project updates (only Admin/Project Manager can assign projects)
    if (team_data.project_ids is not None or team_data.add_project_ids or team_data.remove_project_ids):
        if not check_project_assignment_permission(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and project managers can assign teams to projects"
            )
    
    # Handle complete project replacement
    if team_data.project_ids is not None:
        new_projects = db.query(Project).filter(Project.id.in_(team_data.project_ids)).all()
        if len(new_projects) != len(team_data.project_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more projects not found"
            )
        team.projects = new_projects
    
    # Handle adding specific projects
    if team_data.add_project_ids:
        projects_to_add = db.query(Project).filter(Project.id.in_(team_data.add_project_ids)).all()
        if len(projects_to_add) != len(team_data.add_project_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more projects to add not found"
            )
        # Add projects to team (avoiding duplicates)
        current_project_ids = {project.id for project in team.projects}
        for project in projects_to_add:
            if project.id not in current_project_ids:
                team.projects.append(project)
    
    # Handle removing specific projects
    if team_data.remove_project_ids:
        for project_id in team_data.remove_project_ids:
            # Find and remove project
            project_to_remove = None
            for project in team.projects:
                if project.id == project_id:
                    project_to_remove = project
                    break
            if project_to_remove:
                team.projects.remove(project_to_remove)
    
    db.commit()
    db.refresh(team)
    
    # Reload with all relationships for response
    team = db.query(Team).options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).filter(Team.id == team.id).first()
    
    # Add project count for response
    team.project_count = len(team.projects)
    return team

@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not check_project_assignment_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and project managers can delete teams"
        )
    
    db.delete(team)
    db.commit()

@router.post("/{team_id}/members", response_model=TeamResponse)
def add_team_members(
    team_id: int,
    member_data: TeamMemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add members to team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not check_team_management_permission(current_user, team):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get users to add
    users_to_add = db.query(User).filter(User.id.in_(member_data.user_ids)).all()
    if len(users_to_add) != len(member_data.user_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more users not found"
        )
    
    # Add users to team (avoiding duplicates)
    current_member_ids = {member.id for member in team.members}
    for user in users_to_add:
        if user.id not in current_member_ids:
            team.members.append(user)
    
    db.commit()
    db.refresh(team)
    
    # Reload with all relationships for response
    team = db.query(Team).options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).filter(Team.id == team.id).first()
    
    # Add project count for response
    team.project_count = len(team.projects)
    return team

@router.delete("/{team_id}/members/{user_id}", response_model=TeamResponse)
def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove member from team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not check_team_management_permission(current_user, team):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Cannot remove team leader
    if user_id == team.team_leader_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove team leader from team"
        )
    
    # Find and remove user
    user_to_remove = None
    for member in team.members:
        if member.id == user_id:
            user_to_remove = member
            break
    
    if not user_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not a member of this team"
        )
    
    team.members.remove(user_to_remove)
    db.commit()
    db.refresh(team)
    
    # Reload with all relationships for response
    team = db.query(Team).options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).filter(Team.id == team.id).first()
    
    # Add project count for response
    team.project_count = len(team.projects)
    return team

@router.post("/{team_id}/projects", response_model=TeamResponse)
def assign_team_to_projects(
    team_id: int,
    project_data: TeamProjectAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Assign team to projects (Admin/Project Manager only)"""
    if not check_project_assignment_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and project managers can assign teams to projects"
        )
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Get projects to assign
    projects_to_assign = db.query(Project).filter(Project.id.in_(project_data.project_ids)).all()
    if len(projects_to_assign) != len(project_data.project_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more projects not found"
        )
    
    # Assign projects to team (avoiding duplicates)
    current_project_ids = {project.id for project in team.projects}
    for project in projects_to_assign:
        if project.id not in current_project_ids:
            team.projects.append(project)
    
    db.commit()
    db.refresh(team)
    
    # Reload with all relationships for response
    team = db.query(Team).options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).filter(Team.id == team.id).first()
    
    # Add project count for response
    team.project_count = len(team.projects)
    return team

@router.delete("/{team_id}/projects/{project_id}", response_model=TeamResponse)
def remove_team_from_project(
    team_id: int,
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove team from project"""
    if not check_project_assignment_permission(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and project managers can modify team-project assignments"
        )
    
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    # Find and remove project
    project_to_remove = None
    for project in team.projects:
        if project.id == project_id:
            project_to_remove = project
            break
    
    if not project_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team is not assigned to this project"
        )
    
    team.projects.remove(project_to_remove)
    db.commit()
    db.refresh(team)
    
    # Reload with all relationships for response
    team = db.query(Team).options(
        joinedload(Team.team_leader),
        joinedload(Team.members),
        joinedload(Team.projects)
    ).filter(Team.id == team.id).first()
    
    # Add project count for response
    team.project_count = len(team.projects)
    return team
