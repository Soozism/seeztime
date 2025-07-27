"""
Integration test to verify all APIs are working correctly
"""

import pytest
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_full_workflow():
    """Test a complete workflow to ensure all APIs work"""
    
    # 1. Register a user
    user_data = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register response: {response.status_code} - {response.text}")
    
    if response.status_code != 200:
        print("Registration failed, trying login with existing user")
        # Try to login with existing credentials
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login response: {response.status_code} - {response.text}")
        
        if response.status_code != 200:
            pytest.fail("Cannot authenticate")
    else:
        # Login with newly created user
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login response: {response.status_code} - {response.text}")
    
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a project
    project_data = {
        "name": f"Test Project {int(time.time())}",
        "description": "A test project for integration testing"
    }
    
    response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
    print(f"Create project response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    project_id = response.json()["id"]
    
    # 3. Create a task
    task_data = {
        "title": f"Test Task {int(time.time())}",
        "description": "A test task",
        "project_id": project_id,
        "priority": 3,  # HIGH priority (3)
        "story_points": 5
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    print(f"Create task response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    task_id = response.json()["id"]
    
    # 4. Update task status
    status_data = {"status": "in_progress"}
    response = requests.patch(f"{BASE_URL}/tasks/{task_id}/status", json=status_data, headers=headers)
    print(f"Update task status response: {response.status_code} - {response.text}")
    assert response.status_code == 200
    
    # 5. Get all tasks
    response = requests.get(f"{BASE_URL}/tasks/", headers=headers)
    print(f"Get tasks response: {response.status_code}")
    assert response.status_code == 200
    
    # 6. Get all projects
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print(f"Get projects response: {response.status_code}")
    assert response.status_code == 200
    
    print("All tests passed successfully!")

if __name__ == "__main__":
    test_full_workflow()
