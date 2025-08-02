# Working Hours & Time-Off API Documentation

## Overview

This document provides comprehensive API documentation for the Working Hours and Time-Off management features. These APIs allow administrators and project managers to manage user schedules, holidays, and time-off requests.

## Table of Contents

1. [Working Hours Management](#working-hours-management)
2. [Holiday Management](#holiday-management)
3. [Time-Off Management](#time-off-management)
4. [Data Models](#data-models)
5. [Authentication & Permissions](#authentication--permissions)
6. [Error Handling](#error-handling)
7. [Examples](#examples)

---

## Working Hours Management

### 1. List Working Hours Schedules

**Endpoint:** `GET /api/v1/working-hours/working-hours`

**Purpose:** Retrieve working hours schedules with optional filtering.

**Query Parameters:**
- `user_id` (integer, optional): Filter by specific user ID
- `active_only` (boolean, default: true): Show only active schedules
- `expand` (boolean, default: false): Include user and set_by names in response

**Response:** Array of `WorkingHoursResponse` objects

**Example Request:**
```bash
GET /api/v1/working-hours/working-hours?user_id=3&expand=true&active_only=true
```

**Example Response:**
```json
[
  {
    "id": 17,
    "user_id": 3,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours_per_day": 8,
    "monday_enabled": true,
    "tuesday_enabled": true,
    "wednesday_enabled": true,
    "thursday_enabled": false,
    "friday_enabled": false,
    "saturday_enabled": true,
    "sunday_enabled": true,
    "break_start_time": "12:30:00",
    "break_end_time": "13:30:00",
    "break_duration_minutes": 60,
    "timezone": "Asia/Tehran",
    "effective_from": "2025-03-01",
    "effective_to": null,
    "notes": "Standard Iranian working hours",
    "set_by_id": 1,
    "created_at": "2025-02-28T10:11:00Z",
    "updated_at": null,
    "user_name": "m.reza",
    "user_full_name": "Mohammad Reza",
    "set_by_name": "admin"
  }
]
```

### 2. Create Working Hours Schedule

**Endpoint:** `POST /api/v1/working-hours/working-hours`

**Purpose:** Create a new working hours schedule for a user.

**Request Body:** `WorkingHoursCreate` object

**Required Fields:**
- `user_id` (integer): Target user ID
- `start_time` (time): Work day start time (HH:MM:SS)
- `end_time` (time): Work day end time (HH:MM:SS)
- `effective_from` (date): When this schedule becomes effective

**Optional Fields:**
- `work_hours_per_day` (integer, default: 8): Total working hours per day
- `monday_enabled` (boolean, default: true)
- `tuesday_enabled` (boolean, default: true)
- `wednesday_enabled` (boolean, default: true)
- `thursday_enabled` (boolean, default: false)
- `friday_enabled` (boolean, default: false)
- `saturday_enabled` (boolean, default: true)
- `sunday_enabled` (boolean, default: true)
- `break_start_time` (time): Lunch break start time
- `break_end_time` (time): Lunch break end time
- `break_duration_minutes` (integer, default: 60)
- `timezone` (string, default: "Asia/Tehran")
- `effective_to` (date): When this schedule expires
- `notes` (string): Additional notes

**Example Request:**
```json
{
  "user_id": 3,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "work_hours_per_day": 8,
  "monday_enabled": true,
  "tuesday_enabled": true,
  "wednesday_enabled": true,
  "thursday_enabled": false,
  "friday_enabled": false,
  "saturday_enabled": true,
  "sunday_enabled": true,
  "break_start_time": "12:30:00",
  "break_end_time": "13:30:00",
  "break_duration_minutes": 60,
  "timezone": "Asia/Tehran",
  "effective_from": "2025-09-01",
  "effective_to": null,
  "notes": "Standard Iranian working hours"
}
```

**Example Response (201 Created):**
```json
{
  "id": 18,
  "user_id": 3,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "work_hours_per_day": 8,
  "monday_enabled": true,
  "tuesday_enabled": true,
  "wednesday_enabled": true,
  "thursday_enabled": false,
  "friday_enabled": false,
  "saturday_enabled": true,
  "sunday_enabled": true,
  "break_start_time": "12:30:00",
  "break_end_time": "13:30:00",
  "break_duration_minutes": 60,
  "timezone": "Asia/Tehran",
  "effective_from": "2025-09-01",
  "effective_to": null,
  "notes": "Standard Iranian working hours",
  "set_by_id": 1,
  "created_at": "2025-08-01T21:45:00Z",
  "updated_at": null
}
```

### 3. Get Working Hours by ID

**Endpoint:** `GET /api/v1/working-hours/working-hours/{id}`

**Purpose:** Retrieve a specific working hours schedule.

**Path Parameters:**
- `id` (integer, required): Working hours schedule ID

**Query Parameters:**
- `expand` (boolean, default: false): Include user and set_by names

**Example Request:**
```bash
GET /api/v1/working-hours/working-hours/18?expand=true
```

**Example Response (200 OK):**
```json
{
  "id": 18,
  "user_id": 3,
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "work_hours_per_day": 8,
  "monday_enabled": true,
  "tuesday_enabled": true,
  "wednesday_enabled": true,
  "thursday_enabled": false,
  "friday_enabled": false,
  "saturday_enabled": true,
  "sunday_enabled": true,
  "break_start_time": "12:30:00",
  "break_end_time": "13:30:00",
  "break_duration_minutes": 60,
  "timezone": "Asia/Tehran",
  "effective_from": "2025-09-01",
  "effective_to": null,
  "notes": "Standard Iranian working hours",
  "set_by_id": 1,
  "created_at": "2025-08-01T21:45:00Z",
  "updated_at": null,
  "user_name": "m.reza",
  "user_full_name": "Mohammad Reza",
  "set_by_name": "admin"
}
```

### 4. Update Working Hours Schedule

**Endpoint:** `PUT /api/v1/working-hours/working-hours/{id}`

**Purpose:** Update an existing working hours schedule.

**Path Parameters:**
- `id` (integer, required): Working hours schedule ID

**Request Body:** `WorkingHoursUpdate` object (all fields optional)

**Example Request:**
```json
{
  "start_time": "08:30:00",
  "end_time": "16:30:00",
  "break_start_time": "12:00:00",
  "break_end_time": "13:00:00",
  "notes": "Updated schedule with earlier start time"
}
```

**Example Response (200 OK):**
```json
{
  "id": 18,
  "user_id": 3,
  "start_time": "08:30:00",
  "end_time": "16:30:00",
  "work_hours_per_day": 8,
  "monday_enabled": true,
  "tuesday_enabled": true,
  "wednesday_enabled": true,
  "thursday_enabled": false,
  "friday_enabled": false,
  "saturday_enabled": true,
  "sunday_enabled": true,
  "break_start_time": "12:00:00",
  "break_end_time": "13:00:00",
  "break_duration_minutes": 60,
  "timezone": "Asia/Tehran",
  "effective_from": "2025-09-01",
  "effective_to": null,
  "notes": "Updated schedule with earlier start time",
  "set_by_id": 1,
  "created_at": "2025-08-01T21:45:00Z",
  "updated_at": "2025-08-01T22:00:00Z"
}
```

### 5. Delete Working Hours Schedule

**Endpoint:** `DELETE /api/v1/working-hours/working-hours/{id}`

**Purpose:** Remove a working hours schedule.

**Path Parameters:**
- `id` (integer, required): Working hours schedule ID

**Example Response (200 OK):**
```json
{
  "message": "Working hours deleted successfully"
}
```

### 6. Check Working Day Status

**Endpoint:** `GET /api/v1/working-hours/check-working-day`

**Purpose:** Check if a specific date is a working day for a user.

**Query Parameters:**
- `user_id` (integer, required): User ID to check
- `check_date` (date, required): Date to check (YYYY-MM-DD format)

**Example Request:**
```bash
GET /api/v1/working-hours/check-working-day?user_id=3&check_date=2025-10-14
```

**Example Response (200 OK):**
```json
{
  "user_id": 3,
  "date": "2025-10-14",
  "is_working_day": false,
  "is_holiday": true,
  "is_time_off": false,
  "holiday_name": "عید فطر",
  "working_hours": {
    "id": 18,
    "user_id": 3,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours_per_day": 8,
    "monday_enabled": true,
    "tuesday_enabled": true,
    "wednesday_enabled": true,
    "thursday_enabled": false,
    "friday_enabled": false,
    "saturday_enabled": true,
    "sunday_enabled": true,
    "break_start_time": "12:30:00",
    "break_end_time": "13:30:00",
    "break_duration_minutes": 60,
    "timezone": "Asia/Tehran",
    "effective_from": "2025-09-01",
    "effective_to": null,
    "notes": "Standard Iranian working hours",
    "set_by_id": 1,
    "created_at": "2025-08-01T21:45:00Z",
    "updated_at": null
  }
}
```

### 7. Get User Work Schedule

**Endpoint:** `GET /api/v1/working-hours/users/{user_id}/schedule`

**Purpose:** Get a comprehensive work schedule overview for a user.

**Path Parameters:**
- `user_id` (integer, required): User ID

**Query Parameters:**
- `days_ahead` (integer, default: 30): Number of days to look ahead

**Example Request:**
```bash
GET /api/v1/working-hours/users/3/schedule?days_ahead=60
```

**Example Response (200 OK):**
```json
{
  "user_id": 3,
  "user_name": "m.reza",
  "current_working_hours": {
    "id": 18,
    "user_id": 3,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours_per_day": 8,
    "monday_enabled": true,
    "tuesday_enabled": true,
    "wednesday_enabled": true,
    "thursday_enabled": false,
    "friday_enabled": false,
    "saturday_enabled": true,
    "sunday_enabled": true,
    "break_start_time": "12:30:00",
    "break_end_time": "13:30:00",
    "break_duration_minutes": 60,
    "timezone": "Asia/Tehran",
    "effective_from": "2025-09-01",
    "effective_to": null,
    "notes": "Standard Iranian working hours",
    "set_by_id": 1,
    "created_at": "2025-08-01T21:45:00Z",
    "updated_at": null
  },
  "upcoming_holidays": [
    {
      "id": 45,
      "name": "عید فطر",
      "date": "2025-10-14",
      "calendar_type": "religious",
      "is_national": true,
      "is_recurring": false,
      "jalali_year": null,
      "jalali_month": null,
      "jalali_day": null,
      "description": null,
      "created_by_id": 1,
      "created_at": "2025-08-01T20:00:00Z",
      "updated_at": null,
      "created_by_name": "admin"
    }
  ],
  "pending_time_off": [
    {
      "id": 44,
      "user_id": 3,
      "start_date": "2025-11-02",
      "end_date": "2025-11-03",
      "reason": "Family event",
      "status": "pending",
      "approved_by_id": null,
      "approved_at": null,
      "approval_notes": null,
      "created_at": "2025-08-01T21:30:00Z",
      "updated_at": null,
      "user_name": "m.reza",
      "approved_by_name": null,
      "days_count": 2
    }
  ],
  "approved_time_off": []
}
```

### 8. Get Daily Schedule

**Endpoint:** `GET /api/v1/working-hours/daily-schedule`

**Purpose:** Get day-by-day working status for a user in a date range.

**Query Parameters:**
- `user_id` (integer, required): User ID
- `start_date` (date, required): Start date (YYYY-MM-DD)
- `end_date` (date, required): End date (YYYY-MM-DD)

**Example Request:**
```bash
GET /api/v1/working-hours/daily-schedule?user_id=3&start_date=2025-10-01&end_date=2025-10-31
```

**Example Response (200 OK):**
```json
[
  {
    "date": "2025-10-01",
    "is_working_day": true,
    "is_holiday": false,
    "is_time_off": false,
    "holiday_name": null,
    "time_off_id": null
  },
  {
    "date": "2025-10-02",
    "is_working_day": true,
    "is_holiday": false,
    "is_time_off": false,
    "holiday_name": null,
    "time_off_id": null
  },
  {
    "date": "2025-10-14",
    "is_working_day": false,
    "is_holiday": true,
    "is_time_off": false,
    "holiday_name": "عید فطر",
    "time_off_id": null
  },
  {
    "date": "2025-11-02",
    "is_working_day": false,
    "is_holiday": false,
    "is_time_off": true,
    "holiday_name": null,
    "time_off_id": 44
  }
]
```

### 9. Get User Work Calendar (Alias)

**Endpoint:** `GET /api/v1/working-hours/users/{user_id}/work-calendar`

**Purpose:** Alias for daily-schedule endpoint under user resource.

**Path Parameters:**
- `user_id` (integer, required): User ID

**Query Parameters:**
- `start_date` (date, required): Start date (YYYY-MM-DD)
- `end_date` (date, required): End date (YYYY-MM-DD)

**Response:** Same as daily-schedule endpoint

---

## Holiday Management

### 1. List Holidays

**Endpoint:** `GET /api/v1/working-hours/holidays`

**Purpose:** Retrieve holidays with optional filtering.

**Query Parameters:**
- `year` (integer, optional): Filter by year
- `is_national` (boolean, optional): Filter by national holidays
- `expand` (boolean, default: false): Include creator names

**Example Request:**
```bash
GET /api/v1/working-hours/holidays?year=2025&expand=true
```

**Example Response (200 OK):**
```json
[
  {
    "id": 45,
    "name": "عید فطر",
    "date": "2025-10-14",
    "calendar_type": "religious",
    "is_national": true,
    "is_recurring": false,
    "jalali_year": null,
    "jalali_month": null,
    "jalali_day": null,
    "description": null,
    "created_by_id": 1,
    "created_at": "2025-08-01T20:00:00Z",
    "updated_at": null,
    "created_by_name": "admin"
  },
  {
    "id": 46,
    "name": "جشن نوروز - سال نو",
    "date": "2025-03-21",
    "calendar_type": "national",
    "is_national": true,
    "is_recurring": true,
    "jalali_year": 1404,
    "jalali_month": 1,
    "jalali_day": 1,
    "description": null,
    "created_by_id": 1,
    "created_at": "2025-08-01T20:00:00Z",
    "updated_at": null,
    "created_by_name": "admin"
  }
]
```

### 2. Create Holiday

**Endpoint:** `POST /api/v1/working-hours/holidays`

**Purpose:** Create a custom holiday.

**Request Body:** `HolidayCreate` object

**Required Fields:**
- `name` (string): Holiday name
- `date` (date): Holiday date

**Optional Fields:**
- `calendar_type` (string, default: "national"): "national", "religious", "weekly", "company"
- `is_national` (boolean, default: true)
- `is_recurring` (boolean, default: false)
- `jalali_year` (integer): Jalali year (1300-1500)
- `jalali_month` (integer): Jalali month (1-12)
- `jalali_day` (integer): Jalali day (1-31)
- `description` (string): Holiday description

**Example Request:**
```json
{
  "name": "Company Anniversary",
  "date": "2025-12-15",
  "calendar_type": "company",
  "is_national": false,
  "is_recurring": true,
  "description": "Annual company celebration"
}
```

**Example Response (201 Created):**
```json
{
  "id": 47,
  "name": "Company Anniversary",
  "date": "2025-12-15",
  "calendar_type": "company",
  "is_national": false,
  "is_recurring": true,
  "jalali_year": null,
  "jalali_month": null,
  "jalali_day": null,
  "description": "Annual company celebration",
  "created_by_id": 1,
  "created_at": "2025-08-01T22:30:00Z",
  "updated_at": null
}
```

### 3. Create Multiple Holidays

**Endpoint:** `POST /api/v1/working-hours/holidays/bulk`

**Purpose:** Create multiple holidays at once.

**Request Body:** `BulkHolidayCreate` object

**Example Request:**
```json
{
  "holidays": [
    {
      "name": "New Year's Day",
      "date": "2025-01-01",
      "calendar_type": "national",
      "is_national": true,
      "is_recurring": true
    },
    {
      "name": "Independence Day",
      "date": "2025-07-04",
      "calendar_type": "national",
      "is_national": true,
      "is_recurring": true
    }
  ]
}
```

**Example Response (201 Created):**
```json
[
  {
    "id": 48,
    "name": "New Year's Day",
    "date": "2025-01-01",
    "calendar_type": "national",
    "is_national": true,
    "is_recurring": true,
    "jalali_year": null,
    "jalali_month": null,
    "jalali_day": null,
    "description": null,
    "created_by_id": 1,
    "created_at": "2025-08-01T22:35:00Z",
    "updated_at": null
  },
  {
    "id": 49,
    "name": "Independence Day",
    "date": "2025-07-04",
    "calendar_type": "national",
    "is_national": true,
    "is_recurring": true,
    "jalali_year": null,
    "jalali_month": null,
    "jalali_day": null,
    "description": null,
    "created_by_id": 1,
    "created_at": "2025-08-01T22:35:00Z",
    "updated_at": null
  }
]
```

### 4. Create Iranian Holidays for Year

**Endpoint:** `POST /api/v1/working-hours/holidays/iranian/{year}`

**Purpose:** Automatically create official Iranian holidays for a specific year.

**Path Parameters:**
- `year` (integer, required): Gregorian year (2020-2030)

**Example Request:**
```bash
POST /api/v1/working-hours/holidays/iranian/2025
```

**Example Response (200 OK):**
```json
{
  "message": "Created 25 Iranian holidays for year 2025"
}
```

### 5. Delete Holiday

**Endpoint:** `DELETE /api/v1/working-hours/holidays/{id}`

**Purpose:** Remove a holiday.

**Path Parameters:**
- `id` (integer, required): Holiday ID

**Example Response (200 OK):**
```json
{
  "message": "Holiday deleted successfully"
}
```

---

## Time-Off Management

### 1. List Time-Off Requests

**Endpoint:** `GET /api/v1/time-off/time-off`

**Purpose:** Retrieve time-off requests with optional filtering.

**Query Parameters:**
- `user_id` (integer, optional): Filter by user ID
- `status_filter` (string, optional): Filter by status ("pending", "approved", "rejected")
- `start_date` (date, optional): Filter from start date
- `end_date` (date, optional): Filter to end date
- `expand` (boolean, default: false): Include user and approver names

**Example Request:**
```bash
GET /api/v1/time-off/time-off?user_id=3&status_filter=pending&expand=true
```

**Example Response (200 OK):**
```json
[
  {
    "id": 44,
    "user_id": 3,
    "start_date": "2025-11-02",
    "end_date": "2025-11-03",
    "reason": "Family event",
    "status": "pending",
    "approved_by_id": null,
    "approved_at": null,
    "approval_notes": null,
    "created_at": "2025-08-01T21:30:00Z",
    "updated_at": null,
    "user_name": "m.reza",
    "approved_by_name": null,
    "days_count": 2
  }
]
```

### 2. Create Time-Off Request

**Endpoint:** `POST /api/v1/time-off/time-off`

**Purpose:** Create a new time-off request.

**Request Body:** `TimeOffCreate` object

**Required Fields:**
- `start_date` (date): Start date of time-off
- `end_date` (date): End date of time-off

**Optional Fields:**
- `reason` (string): Reason for time-off
- `user_id` (integer): Target user ID (admin/PM only)

**Example Request:**
```json
{
  "start_date": "2025-11-02",
  "end_date": "2025-11-03",
  "reason": "Family event"
}
```

**Example Response (201 Created):**
```json
{
  "id": 44,
  "user_id": 3,
  "start_date": "2025-11-02",
  "end_date": "2025-11-03",
  "reason": "Family event",
  "status": "pending",
  "approved_by_id": null,
  "approved_at": null,
  "approval_notes": null,
  "created_at": "2025-08-01T21:30:00Z",
  "updated_at": null
}
```

### 3. Get Time-Off Request by ID

**Endpoint:** `GET /api/v1/time-off/time-off/{id}`

**Purpose:** Retrieve a specific time-off request.

**Path Parameters:**
- `id` (integer, required): Time-off request ID

**Query Parameters:**
- `expand` (boolean, default: false): Include user and approver names

**Example Request:**
```bash
GET /api/v1/time-off/time-off/44?expand=true
```

**Example Response (200 OK):**
```json
{
  "id": 44,
  "user_id": 3,
  "start_date": "2025-11-02",
  "end_date": "2025-11-03",
  "reason": "Family event",
  "status": "pending",
  "approved_by_id": null,
  "approved_at": null,
  "approval_notes": null,
  "created_at": "2025-08-01T21:30:00Z",
  "updated_at": null,
  "user_name": "m.reza",
  "approved_by_name": null,
  "days_count": 2
}
```

### 4. Update Time-Off Request

**Endpoint:** `PUT /api/v1/time-off/time-off/{id}`

**Purpose:** Update a time-off request (only pending requests can be edited by users).

**Path Parameters:**
- `id` (integer, required): Time-off request ID

**Request Body:** `TimeOffUpdate` object (all fields optional)

**Example Request:**
```json
{
  "start_date": "2025-11-03",
  "end_date": "2025-11-04",
  "reason": "Updated family event"
}
```

**Example Response (200 OK):**
```json
{
  "id": 44,
  "user_id": 3,
  "start_date": "2025-11-03",
  "end_date": "2025-11-04",
  "reason": "Updated family event",
  "status": "pending",
  "approved_by_id": null,
  "approved_at": null,
  "approval_notes": null,
  "created_at": "2025-08-01T21:30:00Z",
  "updated_at": "2025-08-01T22:00:00Z"
}
```

### 5. Approve Time-Off Request

**Endpoint:** `POST /api/v1/time-off/time-off/{id}/approve`

**Purpose:** Approve a pending time-off request (admin/PM only).

**Path Parameters:**
- `id` (integer, required): Time-off request ID

**Query Parameters:**
- `approval_notes` (string, optional): Notes for approval

**Example Request:**
```bash
POST /api/v1/time-off/time-off/44/approve?approval_notes=Approved for family event
```

**Example Response (200 OK):**
```json
{
  "message": "Time off request approved successfully"
}
```

### 6. Reject Time-Off Request

**Endpoint:** `POST /api/v1/time-off/time-off/{id}/reject`

**Purpose:** Reject a pending time-off request (admin/PM only).

**Path Parameters:**
- `id` (integer, required): Time-off request ID

**Query Parameters:**
- `rejection_reason` (string, required): Reason for rejection

**Example Request:**
```bash
POST /api/v1/time-off/time-off/44/reject?rejection_reason=Insufficient notice period
```

**Example Response (200 OK):**
```json
{
  "message": "Time off request rejected successfully"
}
```

### 7. Delete Time-Off Request

**Endpoint:** `DELETE /api/v1/time-off/time-off/{id}`

**Purpose:** Delete a time-off request (pending requests only, or admin/PM can delete any).

**Path Parameters:**
- `id` (integer, required): Time-off request ID

**Example Response (200 OK):**
```json
{
  "message": "Time off request deleted successfully"
}
```

---

## Data Models

### WorkingHoursCreate
```json
{
  "user_id": "integer (required)",
  "start_time": "time (required) - HH:MM:SS",
  "end_time": "time (required) - HH:MM:SS",
  "work_hours_per_day": "integer (optional, default: 8)",
  "monday_enabled": "boolean (optional, default: true)",
  "tuesday_enabled": "boolean (optional, default: true)",
  "wednesday_enabled": "boolean (optional, default: true)",
  "thursday_enabled": "boolean (optional, default: false)",
  "friday_enabled": "boolean (optional, default: false)",
  "saturday_enabled": "boolean (optional, default: true)",
  "sunday_enabled": "boolean (optional, default: true)",
  "break_start_time": "time (optional) - HH:MM:SS",
  "break_end_time": "time (optional) - HH:MM:SS",
  "break_duration_minutes": "integer (optional, default: 60)",
  "timezone": "string (optional, default: 'Asia/Tehran')",
  "effective_from": "date (required) - YYYY-MM-DD",
  "effective_to": "date (optional) - YYYY-MM-DD",
  "notes": "string (optional)"
}
```

### WorkingHoursResponse
```json
{
  "id": "integer",
  "user_id": "integer",
  "start_time": "time",
  "end_time": "time",
  "work_hours_per_day": "integer",
  "monday_enabled": "boolean",
  "tuesday_enabled": "boolean",
  "wednesday_enabled": "boolean",
  "thursday_enabled": "boolean",
  "friday_enabled": "boolean",
  "saturday_enabled": "boolean",
  "sunday_enabled": "boolean",
  "break_start_time": "time",
  "break_end_time": "time",
  "break_duration_minutes": "integer",
  "timezone": "string",
  "effective_from": "date",
  "effective_to": "date",
  "notes": "string",
  "set_by_id": "integer",
  "created_at": "datetime",
  "updated_at": "datetime",
  "user_name": "string (when expand=true)",
  "user_full_name": "string (when expand=true)",
  "set_by_name": "string (when expand=true)"
}
```

### WorkDayStatus
```json
{
  "date": "date (required) - YYYY-MM-DD",
  "is_working_day": "boolean (required)",
  "is_holiday": "boolean (required)",
  "is_time_off": "boolean (required)",
  "holiday_name": "string (optional)",
  "time_off_id": "integer (optional)"
}
```

### HolidayCreate
```json
{
  "name": "string (required)",
  "date": "date (required) - YYYY-MM-DD",
  "calendar_type": "string (optional, default: 'national') - 'national'|'religious'|'weekly'|'company'",
  "is_national": "boolean (optional, default: true)",
  "is_recurring": "boolean (optional, default: false)",
  "jalali_year": "integer (optional) - 1300-1500",
  "jalali_month": "integer (optional) - 1-12",
  "jalali_day": "integer (optional) - 1-31",
  "description": "string (optional)"
}
```

### TimeOffCreate
```json
{
  "start_date": "date (required) - YYYY-MM-DD",
  "end_date": "date (required) - YYYY-MM-DD",
  "reason": "string (optional)",
  "user_id": "integer (optional) - admin/PM only"
}
```

### TimeOffResponse
```json
{
  "id": "integer",
  "user_id": "integer",
  "start_date": "date",
  "end_date": "date",
  "reason": "string",
  "status": "string - 'pending'|'approved'|'rejected'",
  "approved_by_id": "integer (optional)",
  "approved_at": "datetime (optional)",
  "approval_notes": "string (optional)",
  "created_at": "datetime",
  "updated_at": "datetime",
  "user_name": "string (when expand=true)",
  "approved_by_name": "string (when expand=true)",
  "days_count": "integer (when expand=true)"
}
```

---

## Authentication & Permissions

### Required Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### Role-Based Permissions

#### Admin & Project Manager
- Full access to all working hours features
- Can manage any user's schedule
- Can approve/reject time-off requests
- Can create time-off requests for other users

#### Team Leader
- Can view team members' working hours
- Limited management capabilities

#### Developer/Tester/Viewer
- Can view and manage their own working hours
- Can create time-off requests for themselves
- Cannot approve requests or manage others

### Permission Matrix

| Endpoint | Admin/PM | Team Leader | Developer/Tester/Viewer |
|----------|----------|-------------|-------------------------|
| GET /working-hours/working-hours | All users | Team members | Own only |
| POST /working-hours/working-hours | ✓ | ✗ | ✗ |
| PUT /working-hours/working-hours/{id} | ✓ | ✗ | ✗ |
| DELETE /working-hours/working-hours/{id} | ✓ | ✗ | ✗ |
| GET /working-hours/holidays | ✓ | ✓ | ✓ |
| POST /working-hours/holidays | ✓ | ✗ | ✗ |
| POST /working-hours/holidays/iranian/{year} | ✓ | ✗ | ✗ |
| DELETE /working-hours/holidays/{id} | ✓ | ✗ | ✗ |
| GET /time-off/time-off | All users | Team members | Own only |
| POST /time-off/time-off | ✓ (any user) | ✓ (team members) | ✓ (self only) |
| PUT /time-off/time-off/{id} | ✓ | ✓ (team members) | ✓ (own pending) |
| POST /time-off/time-off/{id}/approve | ✓ | ✗ | ✗ |
| POST /time-off/time-off/{id}/reject | ✓ | ✗ | ✗ |
| DELETE /time-off/time-off/{id} | ✓ | ✓ (team members) | ✓ (own pending) |

---

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (e.g., overlapping schedules)
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### Common Error Scenarios

#### 400 Bad Request
```json
{
  "detail": "Start time must be before end time"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions to view this user's working hours"
}
```

#### 409 Conflict
```json
{
  "detail": "Overlapping working hours schedule exists"
}
```

#### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "start_time"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Examples

### Complete Workflow Example

#### 1. Create Working Hours for a User
```bash
curl -X POST "http://localhost:8000/api/v1/working-hours/working-hours" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 3,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours_per_day": 8,
    "monday_enabled": true,
    "tuesday_enabled": true,
    "wednesday_enabled": true,
    "thursday_enabled": false,
    "friday_enabled": false,
    "saturday_enabled": true,
    "sunday_enabled": true,
    "break_start_time": "12:30:00",
    "break_end_time": "13:30:00",
    "effective_from": "2025-09-01",
    "notes": "Standard Iranian working hours"
  }'
```

#### 2. Create Iranian Holidays for 2025
```bash
curl -X POST "http://localhost:8000/api/v1/working-hours/holidays/iranian/2025" \
  -H "Authorization: Bearer <token>"
```

#### 3. Create Time-Off Request
```bash
curl -X POST "http://localhost:8000/api/v1/time-off/time-off" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-02",
    "end_date": "2025-11-03",
    "reason": "Family event"
  }'
```

#### 4. Approve Time-Off Request
```bash
curl -X POST "http://localhost:8000/api/v1/time-off/time-off/44/approve?approval_notes=Approved" \
  -H "Authorization: Bearer <token>"
```

#### 5. Check Working Day Status
```bash
curl -X GET "http://localhost:8000/api/v1/working-hours/check-working-day?user_id=3&check_date=2025-11-02" \
  -H "Authorization: Bearer <token>"
```

#### 6. Get Daily Schedule
```bash
curl -X GET "http://localhost:8000/api/v1/working-hours/daily-schedule?user_id=3&start_date=2025-11-01&end_date=2025-11-07" \
  -H "Authorization: Bearer <token>"
```

### Python Examples

#### Using requests library
```python
import requests
from datetime import date

# Base configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
headers = {"Authorization": "Bearer <your_token>"}

# Create working hours
working_hours_data = {
    "user_id": 3,
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "work_hours_per_day": 8,
    "monday_enabled": True,
    "tuesday_enabled": True,
    "wednesday_enabled": True,
    "thursday_enabled": False,
    "friday_enabled": False,
    "saturday_enabled": True,
    "sunday_enabled": True,
    "break_start_time": "12:30:00",
    "break_end_time": "13:30:00",
    "effective_from": str(date.today()),
    "notes": "Standard Iranian working hours"
}

response = requests.post(
    f"{API_BASE}/working-hours/working-hours",
    json=working_hours_data,
    headers=headers
)

if response.status_code == 201:
    print("Working hours created successfully")
    working_hours = response.json()
    print(f"Schedule ID: {working_hours['id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Create time-off request
time_off_data = {
    "start_date": "2025-11-02",
    "end_date": "2025-11-03",
    "reason": "Family event"
}

response = requests.post(
    f"{API_BASE}/time-off/time-off",
    json=time_off_data,
    headers=headers
)

if response.status_code == 201:
    print("Time-off request created successfully")
    time_off = response.json()
    print(f"Request ID: {time_off['id']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Get daily schedule
params = {
    "user_id": 3,
    "start_date": "2025-11-01",
    "end_date": "2025-11-07"
}

response = requests.get(
    f"{API_BASE}/working-hours/daily-schedule",
    params=params,
    headers=headers
)

if response.status_code == 200:
    schedule = response.json()
    for day in schedule:
        status = "Working" if day["is_working_day"] else "Off"
        if day["is_holiday"]:
            status = f"Holiday: {day['holiday_name']}"
        elif day["is_time_off"]:
            status = "Time Off"
        print(f"{day['date']}: {status}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

---

## Notes

1. **Time Format**: All time fields use 24-hour format (HH:MM:SS)
2. **Date Format**: All date fields use ISO format (YYYY-MM-DD)
3. **Timezone**: Default timezone is "Asia/Tehran"
4. **Validation**: 
   - Start time must be before end time
   - Break times must be within working hours
   - No overlapping schedules for the same user
   - Time-off dates must be in the future
5. **Iranian Holidays**: Include both solar (Jalali) and lunar (Hijri) holidays
6. **Working Week**: Default is Saturday-Wednesday (Thursday-Friday are holidays)
7. **Status Tracking**: Time-off requests have full audit trail with approval/rejection history 