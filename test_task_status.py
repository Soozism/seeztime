#!/usr/bin/env python3
"""
Test script for task status update endpoint
"""
import requests
import json

def test_task_status_update():
    base_url = "http://localhost:8000"
    
    # Login to get token
    login_response = requests.post(f'{base_url}/api/v1/auth/login', 
        data={'username': 'admin', 'password': 'admin123'})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code} - {login_response.text}")
        return
        
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test updating task status to in_progress
    task_id = 1
    test_cases = [
        {'status': 'in_progress', 'expected': 'Should work'},
        {'status': 'done', 'expected': 'Should work'},
        {'status': 'review', 'expected': 'Should work'},
        {'status': 'todo', 'expected': 'Should work'},
        {'status': 'blocked', 'expected': 'Should work'},
        {'status': 'invalid_status', 'expected': 'Should fail with validation error'}
    ]
    
    for test_case in test_cases:
        print(f"\nTesting status: {test_case['status']} - {test_case['expected']}")
        
        response = requests.patch(
            f'{base_url}/api/v1/tasks/{task_id}/status',
            params={'status': test_case['status']},
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print(f"Success! Task status updated to: {task.get('status')}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    test_task_status_update()
