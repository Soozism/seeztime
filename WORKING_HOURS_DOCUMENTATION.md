# Working Hours Feature Documentation

## Overview

The Working Hours feature allows administrators and project managers to set and manage working schedules for users, including Iranian holidays based on the Jalali calendar and time-off requests.

## Features

### 1. Working Hours Management
- Set daily working hours (start time, end time)
- Configure working days of the week
- Set break times and duration
- Support for Iranian work week (Saturday-Wednesday by default)
- Timezone support (defaults to Asia/Tehran)
- Effective date ranges for schedule changes

### 2. Iranian Holiday Support
- Automatic creation of Iranian national holidays
- Support for Jalali calendar dates
- Weekly holidays (Thursday and Friday by default)
- Recurring yearly holidays (like Nowruz)
- Custom company holidays

### 3. Time Off Management
- Employee time-off requests
- Approval workflow for managers
- Overlap detection
- Status tracking (pending, approved, rejected)

## Database Schema

### WorkingHours Table
- `user_id`: Foreign key to users table
- `start_time`/`end_time`: Daily work hours
- `work_hours_per_day`: Total working hours
- `*_enabled`: Boolean flags for each day of week
- `break_start_time`/`break_end_time`: Break periods
- `timezone`: User timezone
- `effective_from`/`effective_to`: Schedule validity period
- `set_by_id`: Who configured this schedule

### Holiday Table
- `name`: Holiday name
- `date`: Holiday date
- `calendar_type`: `national` | `religious` | `weekly` | `company`
- `is_recurring`: Yearly recurring holidays
- `jalali_year/month/day`: Jalali calendar support (for solar dates)
- **Unique** (`date`, `name`) constraint to prevent duplicates
- `created_by_id`: Who added the holiday

### TimeOff Table
- `user_id`: Employee requesting time off
- `start_date`/`end_date`: Time off period (supports multi-day)
- `reason`: Reason for time off
- `status`: Enum `TimeOffStatus` (`pending`, `approved`, `rejected`)
- `approved_by_id`: Manager who approved/rejected
- `approved_at`: UTC datetime of decision
- `approval_notes`: Notes from manager

## API Endpoints

### Working Hours

#### GET /api/v1/working-hours/working-hours
Get working hours schedules
- **Query Parameters:**
  - `user_id` (optional): Filter by user
  - `active_only` (boolean): Show only active schedules
  - `expand` (boolean): Include user names
- **Permissions:** Admin/PM can view all, users can view their own

#### POST /api/v1/working-hours/working-hours
Create new working hours schedule
- **Body:** WorkingHoursCreate schema
- **Permissions:** Admin/PM only

#### PUT /api/v1/working-hours/working-hours/{id}
Update working hours schedule
- **Body:** WorkingHoursUpdate schema
- **Permissions:** Admin/PM only

#### DELETE /api/v1/working-hours/working-hours/{id}
Delete working hours schedule
- **Permissions:** Admin/PM only

### Holidays

#### GET /api/v1/working-hours/holidays
Get holidays
- **Query Parameters:**
  - `year` (optional): Filter by year
  - `is_national` (optional): Filter national holidays
  - `expand` (boolean): Include creator names

#### POST /api/v1/working-hours/holidays
Create custom holiday
- **Body:** HolidayCreate schema
- **Permissions:** Admin/PM only

#### POST /api/v1/working-hours/holidays/bulk
Create multiple holidays
- **Body:** BulkHolidayCreate schema
- **Permissions:** Admin/PM only

#### POST /api/v1/working-hours/holidays/iranian/{year}
Auto-create Iranian holidays for a year
- **Permissions:** Admin/PM only

#### DELETE /api/v1/working-hours/holidays/{id}
Delete holiday
- **Permissions:** Admin/PM only

### Time Off

#### GET /api/v1/time-off/time-off
Get time off requests
- **Query Parameters:**
  - `user_id` (optional): Filter by user
  - `status_filter` (optional): Filter by status
  - `start_date`/`end_date` (optional): Date range filter
  - `expand` (boolean): Include user names
- **Permissions:** Admin/PM can view all, users can view their own

#### POST /api/v1/time-off/time-off
Create time off request
- **Body:** TimeOffCreate schema
- **Permissions:** Users can create for themselves

#### PUT /api/v1/time-off/time-off/{id}
Update time off request
- **Body:** TimeOffUpdate schema
- **Permissions:** Users can edit their own pending requests, Admin/PM can edit any

#### POST /api/v1/time-off/time-off/{id}/approve
Approve time off request
- **Query Parameters:**
  - `approval_notes` (optional): Notes for approval
- **Permissions:** Admin/PM only

#### POST /api/v1/time-off/time-off/{id}/reject
Reject time off request
- **Query Parameters:**
  - `rejection_reason` (required): Reason for rejection
- **Permissions:** Admin/PM only

#### DELETE /api/v1/time-off/time-off/{id}
Delete time off request
- **Permissions:** Users can delete their own pending requests, Admin/PM can delete any

### Calendar & Utility Endpoints

#### GET /api/v1/working-hours/check-working-day
Check if a specific date is a working day
- **Query Parameters:**
  - `user_id` (required): User to check
  - `check_date` (required): Date to check
- **Returns:** WorkingDayCheck schema with holiday/time-off info

#### GET /api/v1/working-hours/users/{user_id}/schedule
Get complete work schedule for a user
- **Query Parameters:**
  - `days_ahead` (optional): Days to look ahead (default 30)
- **Returns:** UserWorkSchedule with working hours, holidays, time off

#### GET /api/v1/working-hours/daily-schedule
Return day-by-day status for a user in a given date range.
- **Query Parameters:**
  - `user_id` (required)
  - `start_date` (required)
  - `end_date` (required)
- **Returns:** Array of `WorkDayStatus` (date, is_working_day, is_holiday, …)

#### GET /api/v1/working-hours/users/{user_id}/work-calendar
Alias of the previous endpoint nested under user resource. Same parameters/response.

## Permission System

### Roles and Permissions

1. **Admin**
   - Full access to all working hours features
   - Can manage any user's schedule
   - Can approve/reject time off requests

2. **Project Manager**
   - Same as Admin (full access)
   - Can manage team members' schedules
   - Can approve/reject time off requests

3. **Team Leader**
   - Can view team members' working hours
   - Limited management capabilities

4. **Developer/Tester/Viewer**
   - Can view and manage their own working hours
   - Can create time off requests
   - Cannot approve requests or manage others

## Iranian Holiday Support

### Default Holidays Included

1. **Nowruz (Persian New Year)** - 4 days starting Farvardin 1
2. **National Holidays:**
   - Imam Khomeini's Death - Khordad 14
   - June 15 Uprising - Khordad 15
   - Imam Ali's Martyrdom - Tir 30
   - Islamic Revolution Victory - Bahman 22
   - Oil Nationalization Day - Esfand 29

3. **Weekly Holidays:**
   - Thursday (Panj-shanbe)
   - Friday (Jomeh)

### Jalali Calendar Support

The system includes basic Jalali calendar conversion utilities:
- Converting Jalali dates to Gregorian
- Support for recurring holidays based on Jalali calendar
- Leap year calculations for Jalali calendar

**Note:** For production use, consider integrating a proper Jalali calendar library like `jdatetime` or `persiantools`.

## Setup and Migration

### 1. Database Migration
Run the migration to create the new tables:
```bash
cd /path/to/project
python migrate.py  # or alembic upgrade head
```

### 2. Populate Iranian Holidays
Use the provided script to populate default Iranian holidays:
```bash
python populate_iranian_holidays.py
```

### 3. Set Default Working Hours
For existing users, set default working hours:
```python
# Example: Set default Iranian working hours for all users
# Saturday-Wednesday, 9:00-17:00, 1-hour lunch break
```

## Usage Examples

### 1. Set Working Hours for a User
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}
working_hours_data = {
    "user_id": 1,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours_per_day": 8,
    "monday_enabled": True,
    "tuesday_enabled": True,
    "wednesday_enabled": True,
    "thursday_enabled": False,  # Holiday
    "friday_enabled": False,    # Holiday
    "saturday_enabled": True,
    "sunday_enabled": True,
    "break_start_time": "12:00:00",
    "break_end_time": "13:00:00",
    "timezone": "Asia/Tehran",
    "effective_from": "2025-08-01",
    "notes": "Standard Iranian working hours"
}

response = requests.post(
    "http://localhost:8000/api/v1/working-hours/working-hours",
    json=working_hours_data,
    headers=headers
)
```

### 2. Check if Today is a Working Day
```python
response = requests.get(
    "http://localhost:8000/api/v1/working-hours/check-working-day",
    params={
        "user_id": 1,
        "check_date": "2025-08-01"
    },
    headers=headers
)

result = response.json()
if result["is_working_day"]:
    print("Today is a working day")
else:
    print(f"Today is not a working day. Reason: {'Holiday' if result['is_holiday'] else 'Time off' if result['is_time_off'] else 'Non-working day'}")
```

### 3. Create Time Off Request
```python
time_off_data = {
    "start_date": "2025-08-15",
    "end_date": "2025-08-16",
    "reason": "Personal leave"
}

response = requests.post(
    "http://localhost:8000/api/v1/time-off/time-off",
    json=time_off_data,
    headers=headers
)
```

### 4. Approve Time Off Request
```python
response = requests.post(
    "http://localhost:8000/api/v1/time-off/time-off/1/approve",
    params={"approval_notes": "Approved for personal reasons"},
    headers=headers
)
```

## Configuration

### Default Iranian Work Week
By default, the system is configured for the Iranian work week:
- **Working Days:** Saturday, Sunday, Monday, Tuesday, Wednesday
- **Holidays:** Thursday, Friday
- **Standard Hours:** 9:00 AM - 5:00 PM
- **Lunch Break:** 12:00 PM - 1:00 PM

### Timezone Support
- Default timezone: `Asia/Tehran`
- Configurable per user
- All times stored in UTC with timezone information

## Testing

Run the test script to verify the feature:
```bash
python test_working_hours_feature.py
```

This will test:
- Creating working hours
- Managing holidays
- Time off requests
- Working day calculations
- User schedule retrieval

## Future Enhancements

1. **Better Jalali Calendar Support**
   - Integration with proper Jalali calendar libraries
   - More accurate date conversions
   - Support for variable Iranian holidays (religious holidays)

2. **Advanced Scheduling**
   - Flexible working hours (different hours per day)
   - Shift-based working hours
   - Overtime tracking

3. **Integration with Time Tracking**
   - Automatic validation against working hours
   - Overtime alerts
   - Working hours compliance reports

4. **Notifications**
   - Email notifications for time off approvals
   - Reminders for upcoming holidays
   - Working hours violations

5. **Reporting**
   - Working hours compliance reports
   - Time off usage analytics
   - Holiday utilization statistics
