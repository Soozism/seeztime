"""
Test script for Working Hours feature
"""

import requests
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_working_hours_feature():
    """Test the working hours feature"""
    
    print("🕒 Testing Working Hours Feature")
    print("=" * 50)
    
    # First, login to get token
    print("1. Logging in as admin...")
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(f"{API_BASE}/auth/login", data=login_data)
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Test 1: Create working hours for a user
        print("\n2. Creating working hours...")
        working_hours_data = {
            "user_id": 1,  # Assuming user ID 1 exists
            "start_time": "09:00:00",
            "end_time": "17:00:00", 
            "work_hours_per_day": 8,
            "monday_enabled": True,
            "tuesday_enabled": True,
            "wednesday_enabled": True,
            "thursday_enabled": False,  # Holiday in Iran
            "friday_enabled": False,    # Holiday in Iran  
            "saturday_enabled": True,
            "sunday_enabled": True,
            "break_start_time": "12:00:00",
            "break_end_time": "13:00:00",
            "break_duration_minutes": 60,
            "timezone": "Asia/Tehran",
            "effective_from": str(date.today()),
            "notes": "Standard Iranian working hours"
        }
        
        wh_response = requests.post(
            f"{API_BASE}/working-hours/working-hours",
            json=working_hours_data,
            headers=headers
        )
        
        if wh_response.status_code == 201:
            print("✅ Working hours created successfully")
        else:
            print(f"❌ Failed to create working hours: {wh_response.text}")
        
        # Test 2: Get working hours
        print("\n3. Getting working hours...")
        get_wh_response = requests.get(
            f"{API_BASE}/working-hours/working-hours?expand=true",
            headers=headers
        )
        
        if get_wh_response.status_code == 200:
            working_hours = get_wh_response.json()
            print(f"✅ Retrieved {len(working_hours)} working hours records")
            for wh in working_hours[:3]:  # Show first 3
                print(f"   - User: {wh.get('user_name', 'N/A')} | {wh['start_time']} - {wh['end_time']}")
        else:
            print(f"❌ Failed to get working hours: {get_wh_response.text}")
        
        # Test 3: Create Iranian holidays for current year
        print("\n4. Creating Iranian holidays...")
        current_year = date.today().year
        holidays_response = requests.post(
            f"{API_BASE}/working-hours/holidays/iranian/{current_year}",
            headers=headers
        )
        
        if holidays_response.status_code == 200:
            result = holidays_response.json()
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Failed to create holidays: {holidays_response.text}")
        
        # Test 4: Get holidays
        print("\n5. Getting holidays...")
        holidays_response = requests.get(
            f"{API_BASE}/working-hours/holidays?year={current_year}&expand=true",
            headers=headers
        )
        
        if holidays_response.status_code == 200:
            holidays = holidays_response.json()
            print(f"✅ Retrieved {len(holidays)} holidays")
            for holiday in holidays[:5]:  # Show first 5
                print(f"   - {holiday['date']}: {holiday['name']}")
        else:
            print(f"❌ Failed to get holidays: {holidays_response.text}")
        
        # Test 5: Check working day
        print("\n6. Checking if today is a working day...")
        check_response = requests.get(
            f"{API_BASE}/working-hours/check-working-day",
            params={
                "user_id": 1,
                "check_date": str(date.today())
            },
            headers=headers
        )
        
        if check_response.status_code == 200:
            result = check_response.json()
            print(f"✅ Today is {'a working day' if result['is_working_day'] else 'not a working day'}")
            if result['is_holiday']:
                print(f"   🎉 Holiday: {result['holiday_name']}")
        else:
            print(f"❌ Failed to check working day: {check_response.text}")
        
        # Test 6: Create time off request
        print("\n7. Creating time off request...")
        tomorrow = date.today() + timedelta(days=1)
        day_after = date.today() + timedelta(days=2)
        
        time_off_data = {
            "start_date": str(tomorrow),
            "end_date": str(day_after),
            "reason": "Personal leave"
        }
        
        time_off_response = requests.post(
            f"{API_BASE}/time-off/time-off",
            json=time_off_data,
            headers=headers
        )
        
        if time_off_response.status_code == 201:
            print("✅ Time off request created successfully")
            time_off_id = time_off_response.json()["id"]
        else:
            print(f"❌ Failed to create time off request: {time_off_response.text}")
            time_off_id = None
        
        # Test 7: Get user work schedule
        print("\n8. Getting user work schedule...")
        schedule_response = requests.get(
            f"{API_BASE}/working-hours/users/1/schedule",
            headers=headers
        )
        
        if schedule_response.status_code == 200:
            schedule = schedule_response.json()
            print(f"✅ Retrieved work schedule for {schedule['user_name']}")
            print(f"   - Working hours: {bool(schedule['current_working_hours'])}")
            print(f"   - Upcoming holidays: {len(schedule['upcoming_holidays'])}")
            print(f"   - Pending time off: {len(schedule['pending_time_off'])}")
        else:
            print(f"❌ Failed to get work schedule: {schedule_response.text}")
        
        # Test 8: Approve time off (if created)
        if time_off_id:
            print("\n9. Approving time off request...")
            approve_response = requests.post(
                f"{API_BASE}/time-off/time-off/{time_off_id}/approve",
                params={"approval_notes": "Approved for personal reasons"},
                headers=headers
            )
            
            if approve_response.status_code == 200:
                print("✅ Time off request approved successfully")
            else:
                print(f"❌ Failed to approve time off: {approve_response.text}")
        
        print("\n" + "=" * 50)
        print("🎉 Working Hours Feature Test Completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the application is running.")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    test_working_hours_feature()
