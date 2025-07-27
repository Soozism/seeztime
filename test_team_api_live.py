"""
Test the enhanced team creation API with project assignment
"""

import requests
import json

def test_create_team_with_projects():
    """Test creating a team with project assignments"""
    
    print("🧪 Testing Enhanced Team Creation API")
    print("=" * 50)
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # First, let's get an access token (you'll need to authenticate)
    print("📋 Test Data:")
    
    team_data = {
        "name": "Frontend Team",
        "description": "UI/UX Development Team", 
        "team_leader_id": 5,
        "member_ids": [6, 7, 8],
        "project_ids": [1, 2, 3]
    }
    
    print(f"Request URL: POST {base_url}/api/v1/teams/")
    print(f"Request Body:")
    print(json.dumps(team_data, indent=2))
    
    # You'll need to replace this with a valid token
    # To get a token, first authenticate with your admin user
    token = "your_jwt_token_here"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 Making API Request...")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/teams/",
            json=team_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Team created successfully!")
            print(f"Response:")
            print(json.dumps(result, indent=2, default=str))
            
            # Verify the created team has the expected data
            print(f"\n🔍 Verification:")
            print(f"  Team ID: {result.get('id')}")
            print(f"  Team Name: {result.get('name')}")
            print(f"  Team Leader ID: {result.get('team_leader_id')}")
            print(f"  Description: {result.get('description')}")
            
        elif response.status_code == 401:
            print("❌ Authentication failed - Invalid or missing token")
            print("💡 You need to get a valid JWT token first")
            
        elif response.status_code == 403:
            print("❌ Permission denied - User doesn't have permission to create teams")
            print("💡 Only admins and project managers can create teams")
            
        elif response.status_code == 404:
            print("❌ Not found - One or more referenced IDs don't exist")
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"Error: {error_detail}")
            
        elif response.status_code == 422:
            print("❌ Validation error - Invalid request data")
            error_detail = response.json()
            print(f"Validation errors:")
            print(json.dumps(error_detail, indent=2))
            
        else:
            print(f"❌ Unexpected error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error details:")
                print(json.dumps(error_detail, indent=2))
            except:
                print(f"Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Make sure the FastAPI server is running")
        print("💡 Start the server with: python main.py")
        
    except requests.exceptions.Timeout:
        print("❌ Request timeout - Server took too long to respond")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def get_authentication_token():
    """Helper function to get authentication token"""
    
    print("\n🔐 Getting Authentication Token")
    print("-" * 30)
    
    base_url = "http://localhost:8000"
    
    # Default admin credentials (adjust as needed)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"Attempting login with username: {login_data['username']}")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data=login_data,  # Form data for login
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            token = result.get('access_token')
            print("✅ Authentication successful!")
            print(f"Token: {token[:20]}...")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Raw response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - Make sure the FastAPI server is running")
        return None
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return None

def test_with_real_authentication():
    """Test with real authentication"""
    
    print("🚀 Enhanced Team API Test with Authentication")
    print("=" * 60)
    
    # Get authentication token
    token = get_authentication_token()
    
    if not token:
        print("\n💡 Manual token setup required:")
        print("1. Start the FastAPI server: python main.py")
        print("2. Create admin user: python scripts/create_admin.py")
        print("3. Get token via login endpoint or use the token from authentication")
        return
    
    # Test team creation with real token
    base_url = "http://localhost:8000"
    
    team_data = {
        "name": "Frontend Team",
        "description": "UI/UX Development Team", 
        "team_leader_id": 1,  # Adjust based on your user IDs
        "member_ids": [1],    # Adjust based on your user IDs
        "project_ids": [1]    # Adjust based on your project IDs
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 Testing team creation...")
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/teams/",
            json=team_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Team created successfully with project assignments!")
            print("Response:")
            print(json.dumps(result, indent=2, default=str))
        else:
            print("❌ Team creation failed")
            try:
                error = response.json()
                print("Error details:")
                print(json.dumps(error, indent=2))
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f"❌ Error during team creation test: {e}")

if __name__ == "__main__":
    print("Choose test method:")
    print("1. Test with manual token (you provide the JWT token)")
    print("2. Test with automatic authentication")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_create_team_with_projects()
        print("\n💡 Note: Replace 'your_jwt_token_here' in the script with a real token")
    elif choice == "2":
        test_with_real_authentication()
    else:
        print("Invalid choice. Running basic test...")
        test_create_team_with_projects()
