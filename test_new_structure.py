"""
Test the new hierarchical project structure
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_phase_creation():
    """Test creating a phase for a project"""
    
    # First, let's try to get projects to see which ones exist
    projects_response = requests.get(f"{BASE_URL}/projects")
    if projects_response.status_code != 200:
        print("Failed to get projects")
        return
    
    projects = projects_response.json()
    if not projects:
        print("No projects found")
        return
    
    project_id = projects[0]["id"]
    print(f"Using project ID: {project_id}")
    
    # Create a phase
    phase_data = {
        "name": "Planning Phase",
        "description": "Initial planning and requirements gathering",
        "estimated_hours": 80.0,
        "project_id": project_id
    }
    
    phase_response = requests.post(f"{BASE_URL}/phases/", json=phase_data)
    if phase_response.status_code == 201:
        phase = phase_response.json()
        print(f"Phase created successfully: {phase}")
        
        phase_id = phase["id"]
        
        # Create a milestone under this phase
        milestone_data = {
            "name": "Requirements Complete",
            "description": "All requirements documented and approved",
            "estimated_hours": 20.0,
            "phase_id": phase_id
        }
        
        milestone_response = requests.post(f"{BASE_URL}/milestones/", json=milestone_data)
        if milestone_response.status_code == 201:
            milestone = milestone_response.json()
            print(f"Milestone created successfully: {milestone}")
            
            milestone_id = milestone["id"]
            
            # Create a sprint under this milestone
            sprint_data = {
                "name": "Sprint 1 - Requirements",
                "description": "First sprint focusing on requirements",
                "estimated_hours": 20.0,
                "milestone_id": milestone_id
            }
            
            sprint_response = requests.post(f"{BASE_URL}/sprints/", json=sprint_data)
            if sprint_response.status_code == 201:
                sprint = sprint_response.json()
                print(f"Sprint created successfully: {sprint}")
                return True
            else:
                print(f"Failed to create sprint: {sprint_response.status_code} - {sprint_response.text}")
        else:
            print(f"Failed to create milestone: {milestone_response.status_code} - {milestone_response.text}")
    else:
        print(f"Failed to create phase: {phase_response.status_code} - {phase_response.text}")
    
    return False

if __name__ == "__main__":
    print("Testing new hierarchical project structure...")
    success = test_phase_creation()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")
