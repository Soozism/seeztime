"""
Test script to verify expanded API responses work correctly
"""

import requests

# Base URL for the API
BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token"""
    login_data = {
        "username": "admin",  # Default admin user
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_expanded_responses():
    """Test the expanded API responses"""
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Could not authenticate")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🔍 Testing Expanded API Responses...")
    print("=" * 50)
    
    # Test 1: Regular vs Expanded Projects
    print("\n1. Testing Projects - Regular vs Expanded:")
    
    # Regular response
    response = requests.get(f"{BASE_URL}/api/v1/projects/", headers=headers)
    if response.status_code == 200:
        regular_projects = response.json()
        print(f"✅ Regular response: {len(regular_projects)} projects")
        if regular_projects:
            project = regular_projects[0]
            print(f"   Regular keys: {list(project.keys())}")
    
    # Expanded response
    response = requests.get(f"{BASE_URL}/api/v1/projects/?expand=true", headers=headers)
    if response.status_code == 200:
        expanded_projects = response.json()
        print(f"✅ Expanded response: {len(expanded_projects)} projects")
        if expanded_projects:
            project = expanded_projects[0]
            print(f"   Expanded keys: {list(project.keys())}")
            if project.get('created_by_username'):
                print(f"   ✅ Creator: {project.get('created_by_username')} ({project.get('created_by_name', 'No name')})")
            else:
                print(f"   ℹ️  Creator only by ID: {project.get('created_by_id')}")
    
    # Test 2: Regular vs Expanded Tasks
    print("\n2. Testing Tasks - Regular vs Expanded:")
    
    # Regular response
    response = requests.get(f"{BASE_URL}/api/v1/tasks/", headers=headers)
    if response.status_code == 200:
        regular_tasks = response.json()
        print(f"✅ Regular response: {len(regular_tasks)} tasks")
        if regular_tasks:
            task = regular_tasks[0]
            print(f"   Regular keys: {list(task.keys())}")
    
    # Expanded response
    response = requests.get(f"{BASE_URL}/api/v1/tasks/?expand=true", headers=headers)
    if response.status_code == 200:
        expanded_tasks = response.json()
        print(f"✅ Expanded response: {len(expanded_tasks)} tasks")
        if expanded_tasks:
            task = expanded_tasks[0]
            print(f"   Expanded keys: {list(task.keys())}")
            
            # Check expanded fields
            if task.get('project_name'):
                print(f"   ✅ Project: {task.get('project_name')} (ID: {task.get('project_id')})")
            
            if task.get('assignee_username'):
                print(f"   ✅ Assignee: {task.get('assignee_username')} ({task.get('assignee_name', 'No name')})")
            elif task.get('assignee_id'):
                print(f"   ℹ️  Assignee only by ID: {task.get('assignee_id')}")
            else:
                print("   ℹ️  No assignee set")
            
            if task.get('created_by_username'):
                print(f"   ✅ Created by: {task.get('created_by_username')} ({task.get('created_by_name', 'No name')})")
            
            if task.get('sprint_name'):
                print(f"   ✅ Sprint: {task.get('sprint_name')} (ID: {task.get('sprint_id')})")
            elif task.get('sprint_id'):
                print(f"   ℹ️  Sprint only by ID: {task.get('sprint_id')}")
            else:
                print("   ℹ️  No sprint assigned")
    
    # Test 3: Single item with expansion
    print("\n3. Testing Single Item Expansion:")
    
    if expanded_projects:
        project_id = expanded_projects[0]['id']
        
        # Regular single project
        response = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}", headers=headers)
        if response.status_code == 200:
            regular_project = response.json()
            print(f"   Regular single project keys: {list(regular_project.keys())}")
        
        # Expanded single project
        response = requests.get(f"{BASE_URL}/api/v1/projects/{project_id}?expand=true", headers=headers)
        if response.status_code == 200:
            expanded_project = response.json()
            print(f"   Expanded single project keys: {list(expanded_project.keys())}")
    
    print("\n" + "=" * 50)
    print("🎉 Expanded API response testing completed!")

if __name__ == "__main__":
    test_expanded_responses()
