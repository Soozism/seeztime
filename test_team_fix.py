#!/usr/bin/env python3

import requests

# Test the team endpoints now return full project details like members

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzQyODU1OX0.MWYLGP2boYLzEJjcAeQqlr-YB4M8r4QWzXfCMH_GQ2Q"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

# Test 1: Create a team with projects
print("Testing team creation with projects...")
team_data = {
    "name": "Test Team with Project Details",
    "description": "Testing project details in response", 
    "team_leader_id": 1,
    "member_ids": [],
    "project_ids": [1, 2]
}

try:
    response = requests.post(f"{BASE_URL}/api/v1/teams/", json=team_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        result = response.json()
        print(f"Team created with ID: {result['id']}")
        print(f"Project count: {result.get('project_count', 'MISSING')}")
        
        # Check if projects are included in response
        if 'projects' in result:
            print(f"Projects in response: {len(result['projects'])}")
            for project in result['projects']:
                print(f"  - Project {project['id']}: {project['name']} (status: {project['status']})")
        else:
            print("⚠️  No 'projects' field in response")
        
        # Test 2: Get the team to verify project details are included
        print(f"\nTesting GET team/{result['id']} with include_projects=true...")
        get_response = requests.get(f"{BASE_URL}/api/v1/teams/{result['id']}?include_projects=true", headers=headers)
        if get_response.status_code == 200:
            get_result = get_response.json()
            print(f"GET Project count: {get_result.get('project_count', 'MISSING')}")
            
            if 'projects' in get_result:
                print(f"Projects in GET response: {len(get_result['projects'])}")
                for project in get_result['projects']:
                    print(f"  - Project {project['id']}: {project['name']} (status: {project['status']})")
            else:
                print("⚠️  No 'projects' field in GET response")
        else:
            print(f"GET failed: {get_response.status_code} - {get_response.text}")
            
        # Test 3: Get teams list with projects
        print(f"\nTesting GET teams with include_projects=true...")
        list_response = requests.get(f"{BASE_URL}/api/v1/teams/?include_projects=true", headers=headers)
        if list_response.status_code == 200:
            teams = list_response.json()
            print(f"Found {len(teams)} teams")
            for team in teams:
                if team['id'] == result['id']:
                    print(f"Our team has {len(team.get('projects', []))} projects in list response")
                    break
        else:
            print(f"LIST failed: {list_response.status_code} - {list_response.text}")
            
    else:
        print(f"Failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
