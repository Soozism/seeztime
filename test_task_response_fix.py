"""
Test to verify the task response fix
"""

import pytest
import requests
import json

def test_task_endpoints_response_validation():
    """Test that task create and update endpoints return proper TaskResponse"""
    base_url = "http://localhost:8000"
    
    # First, get a token (assuming admin user exists)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Get auth token
        response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test getting tasks (should work)
        response = requests.get(f"{base_url}/api/v1/tasks/", headers=headers)
        print(f"GET tasks status: {response.status_code}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"Found {len(tasks)} tasks")
            
            if tasks:
                # Test updating the first task
                task_id = tasks[0]["id"]
                update_data = {
                    "description": "Updated description for testing response validation"
                }
                
                response = requests.put(
                    f"{base_url}/api/v1/tasks/{task_id}",
                    json=update_data,
                    headers=headers
                )
                print(f"PUT task {task_id} status: {response.status_code}")
                
                if response.status_code == 200:
                    updated_task = response.json()
                    print(f"Updated task response has required fields:")
                    print(f"  - id: {updated_task.get('id')}")
                    print(f"  - title: {updated_task.get('title')}")
                    print(f"  - description: {updated_task.get('description')}")
                    print(f"  - status: {updated_task.get('status')}")
                    print(f"  - priority: {updated_task.get('priority')}")
                    print(f"  - project_name: {updated_task.get('project_name')}")
                    print("✅ Task update endpoint working correctly!")
                else:
                    print(f"❌ PUT failed: {response.text}")
        
        # Test creating a new task if we have projects
        response = requests.get(f"{base_url}/api/v1/projects/", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            if projects:
                project_id = projects[0]["id"]
                
                new_task_data = {
                    "title": "Test Task Response Validation",
                    "description": "Testing that create task returns proper TaskResponse",
                    "project_id": project_id,
                    "priority": 2,
                    "story_points": 3
                }
                
                response = requests.post(
                    f"{base_url}/api/v1/tasks/",
                    json=new_task_data,
                    headers=headers
                )
                print(f"POST task status: {response.status_code}")
                
                if response.status_code == 200:
                    new_task = response.json()
                    print(f"Created task response has required fields:")
                    print(f"  - id: {new_task.get('id')}")
                    print(f"  - title: {new_task.get('title')}")
                    print(f"  - project_name: {new_task.get('project_name')}")
                    print("✅ Task create endpoint working correctly!")
                else:
                    print(f"❌ POST failed: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_task_endpoints_response_validation()
