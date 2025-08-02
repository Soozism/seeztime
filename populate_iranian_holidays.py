"""
Script to populate Iranian holidays for current year
"""

import requests
import sys
from datetime import date

def populate_iranian_holidays():
    """Populate Iranian holidays in the database"""
    
    # Configuration
    BASE_URL = "http://localhost:8000"
    API_BASE = f"{BASE_URL}/api/v1"
    
    print("🇮🇷 Populating Iranian Holidays")
    print("=" * 40)
    
    # Login credentials (change as needed)
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        # Login
        print("Logging in...")
        login_response = requests.post(f"{API_BASE}/auth/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful")
        
        # Get current year
        current_year = date.today().year
        
        # Create Iranian holidays for current year
        print(f"\nCreating Iranian holidays for {current_year}...")
        
        holidays_response = requests.post(
            f"{API_BASE}/working-hours/holidays/iranian/{current_year}",
            headers=headers
        )
        
        if holidays_response.status_code == 200:
            result = holidays_response.json()
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Failed to create holidays: {holidays_response.text}")
            return False
        
        # Also create for next year
        next_year = current_year + 1
        print(f"\nCreating Iranian holidays for {next_year}...")
        
        holidays_response = requests.post(
            f"{API_BASE}/working-hours/holidays/iranian/{next_year}",
            headers=headers
        )
        
        if holidays_response.status_code == 200:
            result = holidays_response.json()
            print(f"✅ {result['message']}")
        else:
            print(f"❌ Failed to create holidays for {next_year}: {holidays_response.text}")
        
        # Get and display created holidays
        print(f"\nRetrieving holidays for {current_year}...")
        
        get_holidays_response = requests.get(
            f"{API_BASE}/working-hours/holidays",
            params={"year": current_year, "expand": True},
            headers=headers
        )
        
        if get_holidays_response.status_code == 200:
            holidays = get_holidays_response.json()
            print(f"✅ Found {len(holidays)} holidays:")
            
            for holiday in holidays[:10]:  # Show first 10
                print(f"   📅 {holiday['date']} - {holiday['name']}")
            
            if len(holidays) > 10:
                print(f"   ... and {len(holidays) - 10} more holidays")
                
        else:
            print(f"❌ Failed to retrieve holidays: {get_holidays_response.text}")
        
        print("\n" + "=" * 40)
        print("🎉 Iranian holidays populated successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the application is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
        return False

if __name__ == "__main__":
    success = populate_iranian_holidays()
    sys.exit(0 if success else 1)
