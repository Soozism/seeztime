#!/usr/bin/env python3
"""
Test script for milestone API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_milestone_api():
    # Login to get token
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful")
    
    # Test milestone creation with proper JSON body
    milestone_data = {
        "name": "Beta Release Milestone",
        "description": "First beta version ready for testing",
        "project_id": 1,
        "due_date": "2025-09-01T00:00:00Z"
    }
    
    print("\n🧪 Testing milestone creation...")
    response = requests.post(f"{BASE_URL}/milestones/", headers=headers, json=milestone_data)
    
    if response.status_code == 201 or response.status_code == 200:
        milestone = response.json()
        print(f"✅ Milestone created successfully: {milestone['name']}")
        milestone_id = milestone['id']
        
        # Test milestone update
        print("\n🧪 Testing milestone update...")
        update_data = {
            "name": "Updated Beta Release",
            "description": "Updated description"
        }
        
        response = requests.put(f"{BASE_URL}/milestones/{milestone_id}", headers=headers, json=update_data)
        
        if response.status_code == 200:
            updated_milestone = response.json()
            print(f"✅ Milestone updated successfully: {updated_milestone['name']}")
        else:
            print(f"❌ Milestone update failed: {response.status_code} - {response.text}")
        
        # Test milestone completion
        print("\n🧪 Testing milestone completion...")
        response = requests.patch(f"{BASE_URL}/milestones/{milestone_id}/complete", headers=headers)
        
        if response.status_code == 200:
            completed_milestone = response.json()
            print(f"✅ Milestone completed successfully: {completed_milestone.get('completed_at')}")
        else:
            print(f"❌ Milestone completion failed: {response.status_code} - {response.text}")
        
        # Test milestone reopen
        print("\n🧪 Testing milestone reopen...")
        response = requests.patch(f"{BASE_URL}/milestones/{milestone_id}/reopen", headers=headers)
        
        if response.status_code == 200:
            reopened_milestone = response.json()
            print(f"✅ Milestone reopened successfully: {reopened_milestone.get('completed_at')}")
        else:
            print(f"❌ Milestone reopen failed: {response.status_code} - {response.text}")
        
    else:
        print(f"❌ Milestone creation failed: {response.status_code} - {response.text}")
    
    # Test getting milestones
    print("\n🧪 Testing milestone retrieval...")
    response = requests.get(f"{BASE_URL}/milestones/", headers=headers)
    
    if response.status_code == 200:
        milestones = response.json()
        print(f"✅ Retrieved {len(milestones)} milestones")
    else:
        print(f"❌ Milestone retrieval failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_milestone_api()
