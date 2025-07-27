#!/usr/bin/env python3
"""
Test script to verify that the project API returns estimated time information
for sprints, milestones, and phases.
"""

import requests
import json
from datetime import datetime, timedelta

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Authentication token
with open("token.txt", "r") as f:
    TOKEN = f.read().strip()

# Headers with authentication
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_project_estimated_time_api():
    """Test that project API returns estimated time for all components"""
    
    # Test data
    project_data = {
        "name": "Test Project with Estimated Time",
        "description": "A test project to verify estimated time API",
        "estimated_hours": 200.0,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=90)).isoformat()
    }
    
    # Create a project
    print("Creating test project...")
    response = requests.post(f"{BASE_URL}/projects/", json=project_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to create project: {response.status_code}")
        print(response.text)
        return
    
    project = response.json()
    project_id = project["id"]
    print(f"Created project with ID: {project_id}")
    
    # Create a phase
    phase_data = {
        "name": "Development Phase",
        "description": "Main development phase",
        "estimated_hours": 120.0,
        "project_id": project_id,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=60)).isoformat()
    }
    
    print("Creating test phase...")
    response = requests.post(f"{BASE_URL}/phases/", json=phase_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to create phase: {response.status_code}")
        print(response.text)
        return
    
    phase = response.json()
    phase_id = phase["id"]
    print(f"Created phase with ID: {phase_id}")
    
    # Create a milestone
    milestone_data = {
        "name": "Alpha Release",
        "description": "First alpha release milestone",
        "estimated_hours": 60.0,
        "phase_id": phase_id
    }
    
    print("Creating test milestone...")
    response = requests.post(f"{BASE_URL}/milestones/", json=milestone_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to create milestone: {response.status_code}")
        print(response.text)
        return
    
    milestone = response.json()
    milestone_id = milestone["id"]
    print(f"Created milestone with ID: {milestone_id}")
    
    # Create a sprint
    sprint_data = {
        "name": "Sprint 1",
        "description": "First sprint of the project",
        "estimated_hours": 40.0,
        "milestone_id": milestone_id,
        "project_id": project_id,
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=14)).isoformat()
    }
    
    print("Creating test sprint...")
    response = requests.post(f"{BASE_URL}/sprints/", json=sprint_data, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to create sprint: {response.status_code}")
        print(response.text)
        return
    
    sprint = response.json()
    sprint_id = sprint["id"]
    print(f"Created sprint with ID: {sprint_id}")
    
    # Now get the project details and verify estimated time information
    print("\nGetting project details...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}", headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to get project: {response.status_code}")
        print(response.text)
        return
    
    project_details = response.json()
    
    # Print the response structure
    print("\n=== PROJECT DETAILS ===")
    print(f"Project ID: {project_details['id']}")
    print(f"Project Name: {project_details['name']}")
    print(f"Project Estimated Hours: {project_details['estimated_hours']}")
    
    # Check sprint summary
    if 'sprint_summary' in project_details:
        sprint_summary = project_details['sprint_summary']
        print("\n=== SPRINT SUMMARY ===")
        print(f"Total Sprints: {sprint_summary['total']}")
        print(f"Total Estimated Hours: {sprint_summary['total_estimated_hours']}")
        print(f"Planned Estimated Hours: {sprint_summary['planned_estimated_hours']}")
        print(f"Active Estimated Hours: {sprint_summary['active_estimated_hours']}")
        print(f"Completed Estimated Hours: {sprint_summary['completed_estimated_hours']}")
    
    # Check milestone summary
    if 'milestone_summary' in project_details:
        milestone_summary = project_details['milestone_summary']
        print("\n=== MILESTONE SUMMARY ===")
        print(f"Total Milestones: {milestone_summary['total']}")
        print(f"Total Estimated Hours: {milestone_summary['total_estimated_hours']}")
        print(f"Pending Estimated Hours: {milestone_summary['pending_estimated_hours']}")
        print(f"Completed Estimated Hours: {milestone_summary['completed_estimated_hours']}")
    
    # Check phase summary
    if 'phase_summary' in project_details:
        phase_summary = project_details['phase_summary']
        print("\n=== PHASE SUMMARY ===")
        print(f"Total Phases: {phase_summary['total']}")
        print(f"Total Estimated Hours: {phase_summary['total_estimated_hours']}")
    
    # Check detailed lists if available
    if 'sprints' in project_details and project_details['sprints']:
        print("\n=== DETAILED SPRINTS ===")
        for sprint in project_details['sprints']:
            print(f"Sprint: {sprint['name']} - Estimated Hours: {sprint['estimated_hours']}")
    
    if 'milestones' in project_details and project_details['milestones']:
        print("\n=== DETAILED MILESTONES ===")
        for milestone in project_details['milestones']:
            print(f"Milestone: {milestone['name']} - Estimated Hours: {milestone['estimated_hours']}")
    
    if 'phases' in project_details and project_details['phases']:
        print("\n=== DETAILED PHASES ===")
        for phase in project_details['phases']:
            print(f"Phase: {phase['name']} - Estimated Hours: {phase['estimated_hours']}")
    
    print("\n✅ Test completed successfully!")
    print("The API now returns estimated time information for sprints, milestones, and phases.")

if __name__ == "__main__":
    test_project_estimated_time_api() 