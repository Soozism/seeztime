"""
Test the enhanced project endpoint with detailed statistics
"""

import requests
import json

def test_enhanced_project_endpoint():
    """Test the enhanced project endpoint"""
    BASE_URL = "http://localhost:8000/api/v1"
    
    # First, try to get an auth token (you'll need to adjust this based on your auth setup)
    login_data = {
        "username": "admin@example.com", 
        "password": "admin123"
    }
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            auth_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        else:
            print("❌ Login failed, testing without auth")
            auth_headers = {}
        
        # Test enhanced project endpoint without details
        print("🧪 Testing enhanced project endpoint (summary only)...")
        response = requests.get(f"{BASE_URL}/projects/1", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Project summary retrieved successfully!")
            print(f"📊 Project: {data.get('name', 'Unknown')}")
            print(f"📈 Task Summary: {json.dumps(data.get('task_summary', {}), indent=2)}")
            print(f"🏃 Sprint Summary: {json.dumps(data.get('sprint_summary', {}), indent=2)}")
            print(f"🎯 Milestone Summary: {json.dumps(data.get('milestone_summary', {}), indent=2)}")
        else:
            print(f"❌ Error getting project summary: {response.status_code}")
            print(response.text)
        
        # Test enhanced project endpoint with details
        print("\n🧪 Testing enhanced project endpoint (with details)...")
        response = requests.get(f"{BASE_URL}/projects/1?include_details=true", headers=auth_headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Project details retrieved successfully!")
            print(f"📝 Tasks Count: {len(data.get('tasks', []))}")
            print(f"🏃 Sprints Count: {len(data.get('sprints', []))}")
            print(f"🎯 Milestones Count: {len(data.get('milestones', []))}")
            
            # Show sample task if available
            if data.get('tasks'):
                sample_task = data['tasks'][0]
                print(f"📋 Sample Task: {sample_task.get('title', 'No title')} - {sample_task.get('status', 'No status')}")
        else:
            print(f"❌ Error getting project details: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    test_enhanced_project_endpoint()
