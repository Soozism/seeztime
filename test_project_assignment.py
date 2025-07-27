"""
Test project assignment and verify database state
"""

import requests
import json

def test_project_assignment():
    """Test project assignment functionality"""
    
    print("🔍 Testing Project Assignment Functionality")
    print("=" * 50)
    
    BASE_URL = "http://localhost:8000"
    
    # Get authentication token
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        auth_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        token = auth_response.json()["access_token"]
        print("✅ Authentication successful!")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Step 1: Check if projects exist
        print("\nStep 1: Checking existing projects...")
        projects_response = requests.get(f"{BASE_URL}/api/v1/projects/", headers=headers)
        
        if projects_response.status_code == 200:
            projects = projects_response.json()
            print(f"Found {len(projects)} projects:")
            for project in projects:
                print(f"  - ID: {project['id']}, Name: {project['name']}")
            
            if len(projects) == 0:
                print("⚠️  No projects found. Creating a test project...")
                
                # Create a test project
                project_data = {
                    "name": "Test Project for Team Assignment",
                    "description": "Test project for verifying team assignment",
                    "status": "active"
                }
                
                create_response = requests.post(f"{BASE_URL}/api/v1/projects/", json=project_data, headers=headers)
                
                if create_response.status_code == 201:
                    new_project = create_response.json()
                    print(f"✅ Created test project: ID {new_project['id']}")
                    project_id = new_project['id']
                else:
                    print(f"❌ Failed to create test project: {create_response.status_code}")
                    return
            else:
                project_id = projects[0]['id']
                
        else:
            print(f"❌ Failed to get projects: {projects_response.status_code}")
            return
        
        # Step 2: Test team creation with valid project ID
        print(f"\nStep 2: Creating team with project ID {project_id}...")
        
        team_data = {
            "name": "Test Team with Projects",
            "description": "Team to test project assignment",
            "team_leader_id": 1,
            "member_ids": [1],
            "project_ids": [project_id]
        }
        
        print("Request Data:")
        print(json.dumps(team_data, indent=2))
        
        team_response = requests.post(f"{BASE_URL}/api/v1/teams/", json=team_data, headers=headers)
        
        print(f"\nResponse Status: {team_response.status_code}")
        
        if team_response.status_code == 201:
            result = team_response.json()
            print("✅ Team created successfully!")
            print("Response:")
            print(json.dumps(result, indent=2, default=str))
            
            team_id = result['id']
            
            # Step 3: Verify project assignment by getting team details
            print(f"\nStep 3: Verifying project assignment for team {team_id}...")
            
            team_detail_response = requests.get(f"{BASE_URL}/api/v1/teams/{team_id}", headers=headers)
            
            if team_detail_response.status_code == 200:
                team_detail = team_detail_response.json()
                project_count = team_detail.get('project_count', 0)
                print(f"Project count in team: {project_count}")
                
                if project_count > 0:
                    print("✅ Project assignment successful!")
                else:
                    print("⚠️  Project assignment may not be working correctly")
                    print("The team was created but project_count is 0")
            
        else:
            error = team_response.json()
            print(f"❌ Team creation failed: {team_response.status_code}")
            print(json.dumps(error, indent=2))
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

def test_team_update_with_projects():
    """Test updating existing team with projects"""
    
    print("\n🔄 Testing Team Update with Projects")
    print("=" * 40)
    
    BASE_URL = "http://localhost:8000"
    
    # Get authentication token
    login_data = {"username": "admin", "password": "admin123"}
    auth_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
    token = auth_response.json()["access_token"]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get existing teams
        teams_response = requests.get(f"{BASE_URL}/api/v1/teams/", headers=headers)
        teams = teams_response.json()
        
        if len(teams) == 0:
            print("No teams found to update")
            return
        
        team_id = teams[0]['id']
        print(f"Testing update on team ID: {team_id}")
        
        # Get projects
        projects_response = requests.get(f"{BASE_URL}/api/v1/projects/", headers=headers)
        projects = projects_response.json()
        
        if len(projects) == 0:
            print("No projects found for assignment")
            return
        
        project_id = projects[0]['id']
        
        # Test updating team with project assignment
        update_data = {
            "name": "Updated Team Name",
            "add_project_ids": [project_id]
        }
        
        print(f"Updating team with project {project_id}...")
        
        update_response = requests.put(f"{BASE_URL}/api/v1/teams/{team_id}", json=update_data, headers=headers)
        
        print(f"Update Response Status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            result = update_response.json()
            print("✅ Team updated successfully!")
            print(f"Project count: {result.get('project_count', 0)}")
        else:
            error = update_response.json()
            print(f"❌ Update failed:")
            print(json.dumps(error, indent=2))
        
    except Exception as e:
        print(f"❌ Update test failed: {e}")

if __name__ == "__main__":
    test_project_assignment()
    test_team_update_with_projects()
