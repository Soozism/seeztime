"""
Test sprint functionality comprehensively
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_sprint_functionality():
    """Test all sprint endpoints"""
    
    # 1. Login as admin
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print("Failed to login")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a project
    project_data = {
        "name": f"Sprint Test Project {int(time.time())}",
        "description": "Test project for sprint functionality"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
    assert response.status_code == 200, f"Failed to create project: {response.text}"
    project_id = response.json()["id"]
    print(f"✓ Created project {project_id}")
    
    # 3. Create a sprint
    sprint_data = {
        "name": f"Test Sprint {int(time.time())}",
        "description": "Test sprint for functionality",
        "project_id": project_id
    }
    response = requests.post(f"{BASE_URL}/sprints/", json=sprint_data, headers=headers)
    assert response.status_code == 200, f"Failed to create sprint: {response.text}"
    sprint_id = response.json()["id"]
    print(f"✓ Created sprint {sprint_id}")
    
    # 4. Create a task
    task_data = {
        "title": f"Test Task {int(time.time())}",
        "description": "Test task for sprint",
        "project_id": project_id,
        "priority": 2,
        "story_points": 3
    }
    response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
    assert response.status_code == 200, f"Failed to create task: {response.text}"
    task_id = response.json()["id"]
    print(f"✓ Created task {task_id}")
    
    # 5. Test start sprint
    response = requests.patch(f"{BASE_URL}/sprints/{sprint_id}/start", headers=headers)
    assert response.status_code == 200, f"Failed to start sprint: {response.text}"
    print(f"✓ Started sprint {sprint_id}")
    
    # 6. Test add task to sprint
    response = requests.post(f"{BASE_URL}/sprints/{sprint_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200, f"Failed to add task to sprint: {response.text}"
    print(f"✓ Added task {task_id} to sprint {sprint_id}")
    
    # 7. Test get sprint tasks
    response = requests.get(f"{BASE_URL}/sprints/{sprint_id}/tasks", headers=headers)
    assert response.status_code == 200, f"Failed to get sprint tasks: {response.text}"
    tasks = response.json()
    assert len(tasks) == 1, f"Expected 1 task, got {len(tasks)}"
    print(f"✓ Retrieved sprint tasks: {len(tasks)} task(s)")
    
    # 8. Test sprint statistics
    response = requests.get(f"{BASE_URL}/sprints/{sprint_id}/statistics", headers=headers)
    assert response.status_code == 200, f"Failed to get sprint statistics: {response.text}"
    stats = response.json()
    assert stats["total_tasks"] == 1, f"Expected 1 task in stats, got {stats['total_tasks']}"
    print(f"✓ Retrieved sprint statistics: {stats['total_tasks']} total tasks")
    
    # 9. Test remove task from sprint
    response = requests.delete(f"{BASE_URL}/sprints/{sprint_id}/tasks/{task_id}", headers=headers)
    assert response.status_code == 200, f"Failed to remove task from sprint: {response.text}"
    print(f"✓ Removed task {task_id} from sprint {sprint_id}")
    
    # 10. Test close sprint
    response = requests.patch(f"{BASE_URL}/sprints/{sprint_id}/close", headers=headers)
    assert response.status_code == 200, f"Failed to close sprint: {response.text}"
    print(f"✓ Closed sprint {sprint_id}")
    
    # 11. Test reopen sprint
    response = requests.patch(f"{BASE_URL}/sprints/{sprint_id}/reopen", headers=headers)
    assert response.status_code == 200, f"Failed to reopen sprint: {response.text}"
    print(f"✓ Reopened sprint {sprint_id}")
    
    print("\n🎉 All sprint functionality tests passed!")

if __name__ == "__main__":
    test_sprint_functionality()
