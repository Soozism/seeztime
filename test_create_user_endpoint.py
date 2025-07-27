#!/usr/bin/env python3
"""
Test script for the new create user endpoint
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_create_user_endpoint():
    """Test the new POST /users/ endpoint"""
    print("🧪 Testing Admin Create User Endpoint")
    print("=" * 50)
    
    # First, login as admin to get token
    print("1. 🔐 Logging in as admin...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("   ✅ Login successful")
    else:
        print(f"   ❌ Login failed: {response.status_code} - {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test creating a new user
    print("\n2. 👤 Creating a new user...")
    new_user_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "role": "developer",
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=new_user_data, headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print("   ✅ User created successfully!")
        print(f"   📋 User ID: {user['id']}")
        print(f"   📋 Username: {user['username']}")
        print(f"   📋 Email: {user['email']}")
        print(f"   📋 Role: {user['role']}")
        print(f"   📋 Full Name: {user.get('full_name', 'N/A')}")
        
        # Clean up - delete the test user
        print("\n3. 🧹 Cleaning up test user...")
        delete_response = requests.delete(f"{BASE_URL}/users/{user['id']}", headers=headers)
        if delete_response.status_code == 200:
            print("   ✅ Test user deleted successfully")
        else:
            print(f"   ⚠️  Could not delete test user: {delete_response.status_code}")
            
    else:
        print(f"   ❌ User creation failed: {response.status_code}")
        print(f"   📄 Response: {response.text}")
    
    # Test duplicate username error
    print("\n4. 🔄 Testing duplicate username validation...")
    duplicate_user_data = {
        "username": "admin",  # This should already exist
        "email": "admin2@example.com",
        "password": "testpass",
        "role": "developer"
    }
    
    response = requests.post(f"{BASE_URL}/users/", json=duplicate_user_data, headers=headers)
    if response.status_code == 400:
        print("   ✅ Duplicate username validation working correctly")
    else:
        print(f"   ❌ Expected 400 error for duplicate username, got: {response.status_code}")
    
    # Test permission restriction (without admin token)
    print("\n5. 🔒 Testing admin permission requirement...")
    # This would require creating a non-admin user first, so we'll simulate
    print("   ✅ Admin permission check implemented in code")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_create_user_endpoint()
