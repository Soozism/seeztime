"""
Test script for the new advanced queries API endpoints
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = None  # Will be set after login

def login_admin():
    """Login as admin to get auth token"""
    login_data = {
        "username": "admin@example.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return f"Bearer {token_data['access_token']}"
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_endpoint(endpoint, description):
    """Test a specific endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"📡 Endpoint: {endpoint}")
    
    headers = {"Authorization": AUTH_TOKEN} if AUTH_TOKEN else {}
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Returned {len(data) if isinstance(data, list) else 1} items")
            if isinstance(data, list) and len(data) > 0:
                print(f"📋 Sample item keys: {list(data[0].keys())}")
            elif isinstance(data, dict):
                print(f"📋 Response keys: {list(data.keys())}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    global AUTH_TOKEN
    
    print("🚀 Starting Advanced Queries API Tests")
    print("=" * 50)
    
    # Login first
    print("\n🔐 Attempting admin login...")
    AUTH_TOKEN = login_admin()
    if not AUTH_TOKEN:
        print("❌ Could not authenticate. Tests cannot proceed.")
        return
    print("✅ Authentication successful!")
    
    # Test dates for filtering
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_params = f"?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
    
    # Test the new advanced query endpoints
    test_endpoints = [
        # Task queries
        ("/queries/tasks/by-sprint/1", "Get tasks by sprint"),
        (f"/queries/tasks/by-sprint/1{date_params}", "Get tasks by sprint with date filter"),
        ("/queries/tasks/by-user/1", "Get tasks by user"),
        (f"/queries/tasks/by-user/1{date_params}", "Get tasks by user with date filter"),
        
        # Sprint queries  
        ("/queries/sprints/by-project/1", "Get sprints by project"),
        (f"/queries/sprints/by-project/1{date_params}", "Get sprints by project with date filter"),
        ("/queries/sprints/by-user/1", "Get sprints by user"),
        
        # Project queries
        ("/queries/projects/by-user/1", "Get projects by user"),
        
        # Time log queries
        ("/queries/time-logs/by-user/1", "Get time logs by user"),
        ("/queries/time-logs/by-task/1", "Get time logs by task"),
        ("/queries/time-logs/by-sprint/1", "Get time logs by sprint"),
        ("/queries/time-logs/by-project/1", "Get time logs by project"),
        
        # Milestone queries
        ("/queries/milestones/by-sprint/1", "Get milestones by sprint"),
        ("/queries/milestones/by-project/1", "Get milestones by project"),
        
        # Summary endpoints
        ("/queries/summary/user/1/time-logs", "Get user time summary"),
        ("/queries/summary/project/1/time-logs", "Get project time summary"),
        ("/queries/summary/sprint/1/time-logs", "Get sprint time summary"),
        
        # Enhanced time logs endpoint
        ("/time-logs/", "Get time logs (enhanced with filters)"),
        (f"/time-logs/{date_params}", "Get time logs with date filter"),
    ]
    
    for endpoint, description in test_endpoints:
        test_endpoint(endpoint, description)
    
    print("\n" + "=" * 50)
    print("🏁 Advanced Queries API Tests Complete!")

if __name__ == "__main__":
    main()
