import pytest
import requests
from datetime import date, timedelta

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

@pytest.mark.skip("Integration test – requires running server and seed data")
def test_daily_schedule_and_work_calendar():
    """Ensure the new calendar endpoints return expected structure."""
    login_resp = requests.post(f"{API_BASE}/auth/login", data={"username": "admin", "password": "admin123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Pick a small range
    start = date.today()
    end = start + timedelta(days=6)

    # /working-hours/daily-schedule
    ds_resp = requests.get(
        f"{API_BASE}/working-hours/daily-schedule",
        params={"user_id": 1, "start_date": str(start), "end_date": str(end)},
        headers=headers,
    )
    assert ds_resp.status_code == 200
    data = ds_resp.json()
    assert len(data) == 7
    first = data[0]
    assert {
        "date",
        "is_working_day",
        "is_holiday",
        "is_time_off",
        "holiday_name",
        "time_off_id",
    }.issubset(first.keys())

    # /users/{id}/work-calendar alias should return identical result
    wc_resp = requests.get(
        f"{API_BASE}/working-hours/users/1/work-calendar",
        params={"start_date": str(start), "end_date": str(end)},
        headers=headers,
    )
    assert wc_resp.status_code == 200
    assert wc_resp.json() == data 