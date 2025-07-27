#!/usr/bin/env python3
"""
Sample script to demonstrate team functionality
"""

import sys
import os
import requests
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

API_BASE = "http://localhost:8000/api/v1"

def get_auth_token():
    """Login and get authentication token"""
    response = requests.post(f"{API_BASE}/auth/login", data={
        "username": "admin",
        "password": "admin123"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def create_sample_data():
    """Create sample team data"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🚀 Creating sample team management data...\n")
    
    # 1. Create users with different roles
    print("👥 Creating users...")
    users_data = [
        {
            "username": "john_leader",
            "email": "john@gingatek.com",
            "password": "password123",
            "first_name": "John",
            "last_name": "Smith",
            "role": "team_leader"
        },
        {
            "username": "alice_dev",
            "email": "alice@gingatek.com", 
            "password": "password123",
            "first_name": "Alice",
            "last_name": "Johnson",
            "role": "developer"
        },
        {
            "username": "bob_tester",
            "email": "bob@gingatek.com",
            "password": "password123",
            "first_name": "Bob",
            "last_name": "Wilson",
            "role": "tester"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        response = requests.post(f"{API_BASE}/users/", json=user_data, headers=headers)
        if response.status_code == 201:
            user = response.json()
            created_users.append(user)
            print(f"   ✅ Created user: {user['username']} ({user['role']})")
        else:
            print(f"   ❌ Failed to create user {user_data['username']}: {response.text}")
    
    # 2. Create a project
    print("\n📁 Creating project...")
    project_data = {
        "name": "E-commerce Platform",
        "description": "Modern e-commerce platform with microservices architecture",
        "start_date": "2025-07-21T00:00:00Z",
        "end_date": "2025-12-31T23:59:59Z"
    }
    
    response = requests.post(f"{API_BASE}/projects/", json=project_data, headers=headers)
    if response.status_code == 201:
        project = response.json()
        print(f"   ✅ Created project: {project['name']}")
        project_id = project['id']
    else:
        print(f"   ❌ Failed to create project: {response.text}")
        return
    
    # 3. Create a team
    print("\n👥 Creating team...")
    team_leader = next((u for u in created_users if u['role'] == 'team_leader'), None)
    team_members = [u['id'] for u in created_users if u['role'] in ['developer', 'tester']]
    
    if team_leader:
        team_data = {
            "name": "Frontend Development Team",
            "description": "Responsible for UI/UX and frontend development",
            "team_leader_id": team_leader['id'],
            "member_ids": team_members
        }
        
        response = requests.post(f"{API_BASE}/teams/", json=team_data, headers=headers)
        if response.status_code == 201:
            team = response.json()
            print(f"   ✅ Created team: {team['name']} (Leader: {team_leader['username']})")
            team_id = team['id']
        else:
            print(f"   ❌ Failed to create team: {response.text}")
            return
    else:
        print("   ❌ No team leader found")
        return
    
    # 4. Assign team to project
    print("\n🔗 Assigning team to project...")
    assignment_data = {"project_ids": [project_id]}
    
    response = requests.post(f"{API_BASE}/teams/{team_id}/projects", json=assignment_data, headers=headers)
    if response.status_code == 200:
        print(f"   ✅ Assigned team to project")
    else:
        print(f"   ❌ Failed to assign team to project: {response.text}")
    
    # 5. Login as team leader and create sprint
    print("\n🏃 Team leader creating sprint...")
    leader_token = None
    response = requests.post(f"{API_BASE}/auth/login", data={
        "username": team_leader['username'],
        "password": "password123"
    })
    if response.status_code == 200:
        leader_token = response.json()["access_token"]
        leader_headers = {"Authorization": f"Bearer {leader_token}"}
        
        sprint_data = {
            "name": "Sprint 1 - User Authentication",
            "description": "Implement user registration, login, and profile management",
            "project_id": project_id,
            "start_date": "2025-07-21T00:00:00Z",
            "end_date": "2025-08-04T23:59:59Z"
        }
        
        response = requests.post(f"{API_BASE}/sprints/", json=sprint_data, headers=leader_headers)
        if response.status_code == 201:
            sprint = response.json()
            print(f"   ✅ Created sprint: {sprint['name']}")
            sprint_id = sprint['id']
        else:
            print(f"   ❌ Failed to create sprint: {response.text}")
            return
    
    # 6. Team leader creates tasks
    print("\n📋 Team leader creating tasks...")
    tasks_data = [
        {
            "title": "User Registration API",
            "description": "Implement user registration endpoint with validation",
            "project_id": project_id,
            "assignee_id": next((u['id'] for u in created_users if u['role'] == 'developer'), None),
            "priority": 3,
            "story_points": 5
        },
        {
            "title": "Login UI Component",
            "description": "Create responsive login form with validation",
            "project_id": project_id,
            "assignee_id": next((u['id'] for u in created_users if u['role'] == 'developer'), None),
            "priority": 3,
            "story_points": 3
        },
        {
            "title": "User Registration Tests",
            "description": "Write comprehensive tests for user registration flow",
            "project_id": project_id,
            "assignee_id": next((u['id'] for u in created_users if u['role'] == 'tester'), None),
            "priority": 2,
            "story_points": 2
        }
    ]
    
    for task_data in tasks_data:
        response = requests.post(f"{API_BASE}/tasks/", json=task_data, headers=leader_headers)
        if response.status_code == 201:
            task = response.json()
            assignee = next((u for u in created_users if u['id'] == task['assignee_id']), None)
            assignee_name = f"{assignee['first_name']} {assignee['last_name']}" if assignee else "Unassigned"
            print(f"   ✅ Created task: {task['title']} (Assigned to: {assignee_name})")
        else:
            print(f"   ❌ Failed to create task {task_data['title']}: {response.text}")
    
    # 7. Team leader creates milestone
    print("\n🎯 Team leader creating milestone...")
    milestone_data = {
        "name": "Authentication Module Complete",
        "description": "User authentication system fully implemented and tested",
        "project_id": project_id,
        "due_date": "2025-08-10T23:59:59Z"
    }
    
    response = requests.post(f"{API_BASE}/milestones/", json=milestone_data, headers=leader_headers)
    if response.status_code == 201:
        milestone = response.json()
        print(f"   ✅ Created milestone: {milestone['name']}")
    else:
        print(f"   ❌ Failed to create milestone: {response.text}")
    
    print("\n🎉 Sample team management data created successfully!")
    print("\n📊 You can now:")
    print("   • View teams at: http://localhost:8000/docs#/teams")
    print("   • Check project assignments")
    print("   • See team-based task management in action")
    print(f"   • Login as team leader: {team_leader['username']} / password123")

if __name__ == "__main__":
    try:
        create_sample_data()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server.")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
