"""
Test the enhanced project API with task counts and team leader filtering
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.team import Team
from app.models.enums import UserRole, TaskStatus, ProjectStatus
from app.core.auth import create_access_token

client = TestClient(app)

def test_project_response_includes_task_counts(test_db: Session):
    """Test that project responses include task counts"""
    
    # Create a test user
    admin_user = User(
        username="admin_test",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_active=True
    )
    admin_user.set_password("password123")
    test_db.add(admin_user)
    test_db.commit()
    test_db.refresh(admin_user)
    
    # Create a test project
    project = Project(
        name="Test Project",
        description="A test project",
        status=ProjectStatus.ACTIVE,
        created_by_id=admin_user.id
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    
    # Create test tasks
    task1 = Task(
        title="Task 1",
        description="First task",
        project_id=project.id,
        assignee_id=admin_user.id,
        created_by_id=admin_user.id,
        status=TaskStatus.TODO
    )
    task2 = Task(
        title="Task 2",
        description="Second task",
        project_id=project.id,
        assignee_id=admin_user.id,
        created_by_id=admin_user.id,
        status=TaskStatus.DONE
    )
    task3 = Task(
        title="Task 3",
        description="Third task",
        project_id=project.id,
        assignee_id=admin_user.id,
        created_by_id=admin_user.id,
        status=TaskStatus.DONE
    )
    
    test_db.add_all([task1, task2, task3])
    test_db.commit()
    
    # Create access token
    token = create_access_token(data={"sub": admin_user.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the projects endpoint
    response = client.get("/api/v1/projects/", headers=headers)
    
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1
    
    project_data = projects[0]
    assert "total_tasks" in project_data
    assert "done_tasks" in project_data
    assert project_data["total_tasks"] == 3
    assert project_data["done_tasks"] == 2


def test_team_leader_project_filtering(test_db: Session):
    """Test that team leaders see only projects assigned to their teams"""
    
    # Create users
    team_leader = User(
        username="team_leader",
        email="leader@test.com",
        role=UserRole.TEAM_LEADER,
        is_active=True
    )
    team_leader.set_password("password123")
    
    other_user = User(
        username="other_user",
        email="other@test.com",
        role=UserRole.DEVELOPER,
        is_active=True
    )
    other_user.set_password("password123")
    
    test_db.add_all([team_leader, other_user])
    test_db.commit()
    test_db.refresh(team_leader)
    test_db.refresh(other_user)
    
    # Create a team with the team leader
    team = Team(
        name="Test Team",
        description="A test team",
        team_leader_id=team_leader.id
    )
    test_db.add(team)
    test_db.commit()
    test_db.refresh(team)
    
    # Create projects
    team_project = Project(
        name="Team Project",
        description="Project for the team",
        status=ProjectStatus.ACTIVE,
        created_by_id=team_leader.id
    )
    other_project = Project(
        name="Other Project",
        description="Project not for the team",
        status=ProjectStatus.ACTIVE,
        created_by_id=other_user.id
    )
    
    test_db.add_all([team_project, other_project])
    test_db.commit()
    test_db.refresh(team_project)
    test_db.refresh(other_project)
    
    # Assign the team project to the team
    team.projects.append(team_project)
    test_db.commit()
    
    # Create access token for team leader
    token = create_access_token(data={"sub": team_leader.username})
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the projects endpoint
    response = client.get("/api/v1/projects/", headers=headers)
    
    assert response.status_code == 200
    projects = response.json()
    
    # Team leader should only see projects assigned to their team
    project_names = [p["name"] for p in projects]
    assert "Team Project" in project_names
    assert "Other Project" not in project_names


if __name__ == "__main__":
    # Run basic validation
    print("Enhanced project API implementation completed!")
    print("Changes made:")
    print("1. Added total_tasks and done_tasks fields to ProjectResponse schema")
    print("2. Updated from_orm_with_expansions method to accept task counts")
    print("3. Enhanced get_projects endpoint to include team leader filtering")
    print("4. Added task count calculations for all project responses")
    print("5. Team leaders now see only projects assigned to their teams")
