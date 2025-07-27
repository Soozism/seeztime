"""
Test sprint with multiple tasks functionality
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_sprint_multiple_tasks():
    """Test that sprints can handle multiple tasks"""
    
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
        "name": f"Multi-Task Sprint Project {int(time.time())}",
        "description": "Test project for multiple tasks in sprint"
    }
    response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
    assert response.status_code == 200, f"Failed to create project: {response.text}"
    project_id = response.json()["id"]
    print(f"✓ Created project {project_id}")
    
    # 3. Create a sprint
    sprint_data = {
        "name": f"Multi-Task Sprint {int(time.time())}",
        "description": "Test sprint with multiple tasks",
        "project_id": project_id
    }
    response = requests.post(f"{BASE_URL}/sprints/", json=sprint_data, headers=headers)
    assert response.status_code == 200, f"Failed to create sprint: {response.text}"
    sprint_id = response.json()["id"]
    print(f"✓ Created sprint {sprint_id}")
    
    # 4. Create multiple tasks (5 tasks)
    task_ids = []
    for i in range(1, 6):
        task_data = {
            "title": f"Task {i} - {int(time.time())}",
            "description": f"Test task number {i}",
            "project_id": project_id,
            "priority": 2,
            "story_points": i
        }
        response = requests.post(f"{BASE_URL}/tasks/", json=task_data, headers=headers)
        assert response.status_code == 200, f"Failed to create task {i}: {response.text}"
        task_id = response.json()["id"]
        task_ids.append(task_id)
        print(f"✓ Created task {i} with ID {task_id}")
    
    # 5. Add tasks to sprint one by one
    print("\\n--- Adding tasks individually ---")
    for i, task_id in enumerate(task_ids[:3], 1):  # Add first 3 tasks individually
        response = requests.post(f"{BASE_URL}/sprints/{sprint_id}/tasks/{task_id}", headers=headers)
        assert response.status_code == 200, f"Failed to add task {task_id} to sprint: {response.text}"
        print(f"✓ Added task {i} (ID: {task_id}) to sprint")
    
    # 6. Add remaining tasks in bulk
    print("\\n--- Adding tasks in bulk ---")
    bulk_data = {
        "task_ids": task_ids[3:]  # Add last 2 tasks in bulk
    }
    response = requests.post(f"{BASE_URL}/sprints/{sprint_id}/tasks/bulk", json=bulk_data, headers=headers)
    assert response.status_code == 200, f"Failed to add tasks in bulk: {response.text}"
    bulk_result = response.json()
    print(f"✓ Added {bulk_result['added_count']} tasks in bulk: {bulk_data['task_ids']}")
    
    # 7. Verify all tasks are in the sprint
    response = requests.get(f"{BASE_URL}/sprints/{sprint_id}/tasks", headers=headers)
    assert response.status_code == 200, f"Failed to get sprint tasks: {response.text}"
    sprint_tasks = response.json()
    sprint_task_ids = [task["id"] for task in sprint_tasks]
    
    print(f"\\n--- Sprint Task Verification ---")
    print(f"✓ Sprint now contains {len(sprint_tasks)} tasks")
    print(f"✓ Expected task IDs: {sorted(task_ids)}")
    print(f"✓ Actual task IDs: {sorted(sprint_task_ids)}")
    
    # Verify all our tasks are in the sprint
    assert len(sprint_tasks) == 5, f"Expected 5 tasks in sprint, got {len(sprint_tasks)}"
    for task_id in task_ids:
        assert task_id in sprint_task_ids, f"Task {task_id} not found in sprint"
    
    # 8. Get sprint statistics
    response = requests.get(f"{BASE_URL}/sprints/{sprint_id}/statistics", headers=headers)
    assert response.status_code == 200, f"Failed to get sprint statistics: {response.text}"
    stats = response.json()
    
    print(f"\\n--- Sprint Statistics ---")
    print(f"✓ Total tasks: {stats['total_tasks']}")
    print(f"✓ Total story points: {stats['total_story_points']}")
    print(f"✓ Completed tasks: {stats['completed_tasks']}")
    print(f"✓ In progress tasks: {stats['in_progress_tasks']}")
    print(f"✓ Todo tasks: {stats['todo_tasks']}")
    
    assert stats['total_tasks'] == 5, f"Expected 5 tasks in stats, got {stats['total_tasks']}"
    assert stats['total_story_points'] == 15, f"Expected 15 story points (1+2+3+4+5), got {stats['total_story_points']}"
    
    # 9. Remove some tasks in bulk
    print("\\n--- Removing tasks in bulk ---")
    remove_bulk_data = {
        "task_ids": task_ids[:2]  # Remove first 2 tasks
    }
    print(f"Attempting to remove tasks: {remove_bulk_data['task_ids']}")
    print(f"Using headers: {headers}")
    response = requests.delete(f"{BASE_URL}/sprints/{sprint_id}/tasks/bulk", json=remove_bulk_data, headers=headers)
    print(f"DELETE response status: {response.status_code}")
    print(f"DELETE response text: {response.text}")
    assert response.status_code == 200, f"Failed to remove tasks in bulk: {response.text}"
    remove_result = response.json()
    print(f"✓ Removed {remove_result['removed_count']} tasks in bulk")
    
    # 10. Verify tasks were removed
    response = requests.get(f"{BASE_URL}/sprints/{sprint_id}/tasks", headers=headers)
    assert response.status_code == 200, f"Failed to get sprint tasks after removal: {response.text}"
    remaining_tasks = response.json()
    
    print(f"\\n--- Final Verification ---")
    print(f"✓ Sprint now contains {len(remaining_tasks)} tasks (should be 3)")
    assert len(remaining_tasks) == 3, f"Expected 3 tasks remaining, got {len(remaining_tasks)}"
    
    print("\\n🎉 Sprint multiple tasks functionality works perfectly!")
    print("✅ Sprints can handle multiple tasks")
    print("✅ Individual task addition works")
    print("✅ Bulk task addition works")
    print("✅ Bulk task removal works")
    print("✅ Task counting and statistics work correctly")

if __name__ == "__main__":
    test_sprint_multiple_tasks()
