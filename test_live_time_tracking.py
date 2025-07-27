"""
Test the new live time tracking functionality
"""

import requests
import time
import json

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Token (you need to get this from login)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc1MzE5NjU3Nn0.OQB84-AQi40m-MHaKQ6pnd5rngymVDPLUOsU4LpXDUE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_live_time_tracking():
    """Test the complete live time tracking flow"""
    
    # Step 1: Start timer for task 1
    print("🚀 Starting timer for task 1...")
    response = requests.post(f"{BASE_URL}/time-logs/start-timer?task_id=1", headers=headers)
    
    if response.status_code == 200:
        timer_data = response.json()
        print(f"✅ Timer started: {timer_data}")
        timer_id = timer_data["timer_id"]
    else:
        print(f"❌ Failed to start timer: {response.status_code} - {response.text}")
        return
    
    # Step 2: Get active timer status
    print("\n📊 Getting active timer status...")
    response = requests.get(f"{BASE_URL}/time-logs/active-timer", headers=headers)
    
    if response.status_code == 200:
        active_timer = response.json()
        print(f"✅ Active timer: {active_timer}")
        print(f"   Elapsed time: {active_timer['elapsed_seconds']} seconds")
    else:
        print(f"❌ Failed to get active timer: {response.status_code} - {response.text}")
    
    # Step 3: Wait a few seconds to simulate work
    print("\n⏳ Simulating 5 seconds of work...")
    time.sleep(5)
    
    # Step 4: Get updated timer status
    print("\n📊 Getting updated timer status...")
    response = requests.get(f"{BASE_URL}/time-logs/active-timer", headers=headers)
    
    if response.status_code == 200:
        active_timer = response.json()
        print(f"✅ Updated timer: Elapsed {active_timer['elapsed_seconds']} seconds")
    else:
        print(f"❌ Failed to get updated timer: {response.status_code} - {response.text}")
    
    # Step 5: Stop timer
    print("\n🛑 Stopping timer...")
    stop_data = {
        "timer_id": timer_id,
        "description": "Test live time tracking session"
    }
    response = requests.post(f"{BASE_URL}/time-logs/stop-timer", headers=headers, json=stop_data)
    
    if response.status_code == 200:
        stop_result = response.json()
        print(f"✅ Timer stopped: {stop_result}")
        time_log_id = stop_result["time_log_id"]
    else:
        print(f"❌ Failed to stop timer: {response.status_code} - {response.text}")
        return
    
    # Step 6: Get task with time logs
    print("\n📋 Getting task with time logs...")
    response = requests.get(f"{BASE_URL}/tasks/1?include_time_logs=true", headers=headers)
    
    if response.status_code == 200:
        task_data = response.json()
        print(f"✅ Task data retrieved")
        if "time_logs" in task_data:
            print(f"   Time logs count: {len(task_data['time_logs'])}")
            print(f"   Latest time log: {task_data['time_logs'][-1] if task_data['time_logs'] else 'None'}")
        else:
            print("   No time logs field found")
    else:
        print(f"❌ Failed to get task: {response.status_code} - {response.text}")
    
    print("\n🎉 Live time tracking test completed!")

if __name__ == "__main__":
    test_live_time_tracking()
