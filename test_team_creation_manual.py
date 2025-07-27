"""
Quick manual test for the enhanced team creation API
"""

import requests
import json

def test_team_creation():
    """Test the team creation API endpoint"""
    
    print("🧪 Testing Enhanced Team Creation API")
    print("=" * 50)
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    
    # Step 1: Get authentication token
    print("Step 1: Getting authentication token...")
    
    login_data = {
        "username": "admin",  # Change to your admin username
        "password": "admin123"  # Change to your admin password
    }
    
    try:
        auth_response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=login_data)
        
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            print("✅ Authentication successful!")
        else:
            print(f"❌ Authentication failed: {auth_response.status_code}")
            print("Make sure you have created an admin user and the server is running")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure FastAPI is running on localhost:8000")
        print("Run: python main.py")
        return
    
    # Step 2: Test team creation with projects
    print("\nStep 2: Creating team with project assignments...")
    
    team_data = {
        "name": "Frontend Team",
        "description": "UI/UX Development Team",
        "team_leader_id": 1,  # Adjust this to a valid user ID
        "member_ids": [1],    # Adjust these to valid user IDs  
        "project_ids": [1]    # Adjust these to valid project IDs
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("Request Data:")
    print(json.dumps(team_data, indent=2))
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/teams/", json=team_data, headers=headers)
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Team created successfully!")
            print("Response:")
            print(json.dumps(result, indent=2, default=str))
            
        elif response.status_code == 404:
            error = response.json()
            print("❌ Some referenced IDs don't exist:")
            print(f"Error: {error['detail']}")
            print("\n💡 Make sure you have:")
            print("- Valid user IDs for team_leader_id and member_ids")
            print("- Valid project IDs for project_ids")
            
        elif response.status_code == 403:
            print("❌ Permission denied - only admins/project managers can create teams")
            
        else:
            error = response.json()
            print(f"❌ Error: {response.status_code}")
            print(json.dumps(error, indent=2))
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def show_setup_instructions():
    """Show setup instructions"""
    
    print("📋 Setup Instructions for Testing")
    print("=" * 40)
    print()
    print("1. Start the FastAPI server:")
    print("   python main.py")
    print()
    print("2. Create admin user (if not already created):")
    print("   python scripts/create_admin.py")
    print()
    print("3. Create some test users and projects in the database")
    print("   (You can use the admin interface or create them via API)")
    print()
    print("4. Update the IDs in this test script:")
    print("   - team_leader_id: Use a valid user ID with TEAM_LEADER role")
    print("   - member_ids: Use valid user IDs") 
    print("   - project_ids: Use valid project IDs")
    print()
    print("5. Run this test:")
    print("   python test_team_api_live.py")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Run the test")
    print("2. Show setup instructions")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_team_creation()
    elif choice == "2":
        show_setup_instructions()
    else:
        print("Invalid choice")
        show_setup_instructions()
