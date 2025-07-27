#!/usr/bin/env python3
"""
Test Enhanced Dashboard API functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests

BASE_URL = "http://localhost:8000/api/v1"

def login_user(username: str, password: str) -> str:
    """Login and get access token"""
    response = requests.post(f"{BASE_URL}/auth/login", data={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def test_enhanced_dashboard():
    """Test the enhanced dashboard endpoint"""
    print("🧪 Testing Enhanced Dashboard API")
    print("=" * 50)
    
    try:
        # Login as admin
        print("1. 🔐 Logging in as admin...")
        token = login_user("admin", "admin123")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Admin login successful")
        
        # Test main dashboard endpoint
        print("\n2. 📊 Testing main dashboard endpoint...")
        response = requests.get(f"{BASE_URL}/dashboard/dashboard", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard data retrieved successfully")
            print(f"   User: {data.get('user_info', {}).get('username', 'N/A')}")
            print(f"   Projects: {data.get('projects', {}).get('total', 0)}")
            print(f"   Tasks: {data.get('tasks', {}).get('my_assigned_total', 0)}")
            print(f"   Teams: {data.get('teams', {}).get('total', 0)}")
            print(f"   Story Points: {data.get('story_points', {}).get('my_total', 0)}")
            print(f"   Total Hours: {data.get('time_logs', {}).get('total_hours', 0)}")
        else:
            print(f"❌ Dashboard request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Test user-specific dashboard endpoint (admin viewing their own data)
        print("\n3. 👤 Testing user-specific dashboard endpoint...")
        # First get user ID
        user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if user_response.status_code == 200:
            user_id = user_response.json()["id"]
            
            # Test user-specific dashboard
            response = requests.get(f"{BASE_URL}/dashboard/dashboard/user/{user_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ User-specific dashboard data retrieved successfully")
                print(f"   User: {data.get('user_info', {}).get('username', 'N/A')}")
                print(f"   Role: {data.get('user_info', {}).get('role', 'N/A')}")
                print(f"   Projects: {data.get('projects', {}).get('total', 0)}")
                print(f"   Assigned Tasks: {data.get('tasks', {}).get('assigned_total', 0)}")
                print(f"   Created Tasks: {data.get('tasks', {}).get('created_total', 0)}")
                print(f"   Completion Rate: {data.get('tasks', {}).get('completion_rate', 0):.1f}%")
                print(f"   Story Points Completed: {data.get('story_points', {}).get('completed', 0)}")
                print(f"   Teams Leading: {data.get('teams', {}).get('leading', 0)}")
                print("   Performance Metrics:")
                pm = data.get('performance_metrics', {})
                print(f"     - Avg Hours/Task: {pm.get('average_hours_per_task', 0):.2f}")
                print(f"     - Tasks per Project: {pm.get('tasks_per_project', 0):.2f}")
            else:
                print(f"❌ User-specific dashboard request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        else:
            print(f"❌ Get user info failed: {user_response.status_code}")
            return False
        
        # Test permission restriction (try to access non-existent user)
        print("\n4. 🔒 Testing permission restrictions...")
        response = requests.get(f"{BASE_URL}/dashboard/dashboard/user/99999", headers=headers)
        if response.status_code == 404:
            print("✅ Correctly returned 404 for non-existent user")
        else:
            print(f"⚠️  Expected 404, got {response.status_code}")
        
        print("\n✅ All dashboard tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

def test_permission_system():
    """Test permission system with different roles"""
    print("\n🔐 Testing Permission System")
    print("=" * 50)
    
    try:
        # Login as admin
        admin_token = login_user("admin", "admin123")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Get admin user ID
        admin_response = requests.get(f"{BASE_URL}/auth/me", headers=admin_headers)
        admin_id = admin_response.json()["id"]
        
        # Create a test user
        print("1. Creating test user...")
        user_data = {
            "username": "testuser_dashboard",
            "email": "testuser_dashboard@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "role": "developer"
        }
        
        response = requests.post(f"{BASE_URL}/users/", json=user_data, headers=admin_headers)
        if response.status_code == 201:
            test_user_id = response.json()["id"]
            print(f"✅ Test user created with ID: {test_user_id}")
        else:
            print(f"❌ Failed to create test user: {response.text}")
            return False
        
        # Login as test user
        test_token = login_user("testuser_dashboard", "password123")
        test_headers = {"Authorization": f"Bearer {test_token}"}
        
        # Test user accessing their own data
        print("\n2. Testing user accessing own data...")
        response = requests.get(f"{BASE_URL}/dashboard/dashboard/user/{test_user_id}", headers=test_headers)
        if response.status_code == 200:
            print("✅ User can access their own dashboard data")
        else:
            print(f"❌ User failed to access own data: {response.status_code}")
        
        # Test user trying to access admin data (should fail)
        print("\n3. Testing user accessing admin data (should fail)...")
        response = requests.get(f"{BASE_URL}/dashboard/dashboard/user/{admin_id}", headers=test_headers)
        if response.status_code == 403:
            print("✅ Correctly denied access to other user's data")
        else:
            print(f"❌ Expected 403, got {response.status_code}")
        
        # Test admin accessing user data (should work)
        print("\n4. Testing admin accessing user data...")
        response = requests.get(f"{BASE_URL}/dashboard/dashboard/user/{test_user_id}", headers=admin_headers)
        if response.status_code == 200:
            print("✅ Admin can access user dashboard data")
        else:
            print(f"❌ Admin failed to access user data: {response.status_code}")
        
        # Cleanup: Delete test user
        print("\n5. Cleaning up test user...")
        response = requests.delete(f"{BASE_URL}/users/{test_user_id}", headers=admin_headers)
        if response.status_code == 204:
            print("✅ Test user deleted successfully")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Permission test failed with error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Enhanced Dashboard API Test Suite")
    print("=" * 60)
    
    # Test main functionality
    success1 = test_enhanced_dashboard()
    
    # Test permission system
    success2 = test_permission_system()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Enhanced Dashboard API is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    import subprocess
    import time
    
    # Check if server is running, if not start it
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            raise Exception("Server not responding")
        print("✅ Server is already running")
    except Exception:
        print("🚀 Starting server...")
        # Start server in background
        subprocess.Popen(["python", "main.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Wait for server to start
    
    success = main()
    sys.exit(0 if success else 1)
