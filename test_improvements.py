"""
Test script to verify the new model improvements and API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_api_endpoints():
    """Test that all endpoints are accessible (will get 401 without auth, which is expected)"""
    
    endpoints_to_test = [
        # Existing endpoints
        "/auth/login",
        "/users/",
        "/projects/",
        "/tasks/",
        "/sprints/",
        "/bug-reports/",
        "/time-logs/",
        "/teams/",
        "/milestones/",
        "/dashboard/overview",
        
        # New endpoints we added
        "/dependencies/task/1/dependencies",
        "/versions/project/1/versions", 
        "/tags/",
        "/tags/categories/",
    ]
    
    print("Testing API endpoints availability...")
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "✅ Available" if response.status_code in [200, 401, 422] else f"❌ Error ({response.status_code})"
            print(f"{endpoint}: {status}")
        except requests.exceptions.RequestException as e:
            print(f"{endpoint}: ❌ Connection error")
    
    print("\n" + "="*50)
    print("✅ API endpoint test completed!")
    print("Note: 401 responses are expected without authentication")
    print("Note: 422 responses are expected for endpoints requiring path parameters")

if __name__ == "__main__":
    test_api_endpoints()
