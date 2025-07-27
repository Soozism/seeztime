"""
Test the enhanced team update API with project management
"""

import requests
import json

def test_team_update_project_operations():
    """Test all project operations in team update API"""
    
    print("🧪 Testing Enhanced Team Update API - Project Operations")
    print("=" * 60)
    
    BASE_URL = "http://localhost:8000"
    
    # Get authentication
    login_data = {"username": "admin", "password": "admin123"}
    auth_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    token = auth_response.json()["access_token"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get existing teams and projects
        teams_response = requests.get(f"{BASE_URL}/api/v1/teams/", headers=headers)
        projects_response = requests.get(f"{BASE_URL}/api/v1/projects/", headers=headers)
        
        teams = teams_response.json()
        projects = projects_response.json()
        
        if len(teams) == 0 or len(projects) < 2:
            print("❌ Need at least 1 team and 2 projects for testing")
            return
        
        team_id = teams[0]['id']
        project1_id = projects[0]['id']
        project2_id = projects[1]['id']
        
        print(f"Using Team ID: {team_id}")
        print(f"Using Project IDs: {project1_id}, {project2_id}")
        
        # Test 1: Add projects to team
        print("\n📋 Test 1: Adding projects to team...")
        update_data = {
            "add_project_ids": [project1_id, project2_id]
        }
        
        response = requests.put(f"{BASE_URL}/api/v1/teams/{team_id}", json=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Projects added! Project count: {result.get('project_count', 0)}")
        else:
            print(f"❌ Failed: {response.json()}")
            return
        
        # Test 2: Remove one project
        print("\n📋 Test 2: Removing one project...")
        update_data = {
            "remove_project_ids": [project1_id]
        }
        
        response = requests.put(f"{BASE_URL}/api/v1/teams/{team_id}", json=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Project removed! Project count: {result.get('project_count', 0)}")
        else:
            print(f"❌ Failed: {response.json()}")
            return
        
        # Test 3: Replace all projects
        print("\n📋 Test 3: Replacing all projects...")
        update_data = {
            "project_ids": [project1_id]  # Replace with just one project
        }
        
        response = requests.put(f"{BASE_URL}/api/v1/teams/{team_id}", json=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Projects replaced! Project count: {result.get('project_count', 0)}")
        else:
            print(f"❌ Failed: {response.json()}")
            return
        
        # Test 4: Combined operation (members + projects)
        print("\n📋 Test 4: Combined member and project update...")
        update_data = {
            "name": "Updated Team via API Test",
            "description": "Team updated with combined operations",
            "add_project_ids": [project2_id]
        }
        
        response = requests.put(f"{BASE_URL}/api/v1/teams/{team_id}", json=update_data, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Combined update successful!")
            print(f"   New name: {result.get('name')}")
            print(f"   Project count: {result.get('project_count', 0)}")
        else:
            print(f"❌ Failed: {response.json()}")
            
        print("\n🎉 All update API tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def show_update_api_capabilities():
    """Show all available update operations"""
    
    print("📋 Enhanced Team Update API Capabilities")
    print("=" * 50)
    print()
    print("🔧 AVAILABLE PROJECT OPERATIONS:")
    print()
    print("1️⃣ ADD PROJECTS:")
    print("PUT /api/v1/teams/{team_id}")
    print('{"add_project_ids": [4, 5, 6]}')
    print()
    print("2️⃣ REMOVE PROJECTS:")
    print("PUT /api/v1/teams/{team_id}")
    print('{"remove_project_ids": [1, 2]}')
    print()
    print("3️⃣ REPLACE ALL PROJECTS:")
    print("PUT /api/v1/teams/{team_id}")
    print('{"project_ids": [7, 8, 9]}')
    print()
    print("4️⃣ COMBINED OPERATIONS:")
    print("PUT /api/v1/teams/{team_id}")
    print('''{
  "name": "New Team Name",
  "add_member_ids": [10, 11],
  "remove_member_ids": [3],
  "add_project_ids": [12, 13],
  "remove_project_ids": [4]
}''')
    print()
    print("🔐 PERMISSIONS:")
    print("- Team Info & Members: Team leaders can update their own teams")
    print("- Project Assignments: Only Admins/Project Managers")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Test the update API")
    print("2. Show update API capabilities")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_team_update_project_operations()
    elif choice == "2":
        show_update_api_capabilities()
    else:
        show_update_api_capabilities()
