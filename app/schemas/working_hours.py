"""
Working Hours schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime, date, time

from app.models.enums import TimeOffStatus, CalendarType

class WorkingHoursBase(BaseModel):
    start_time: time = Field(..., description="Start time of work day (e.g., 09:00)")
    end_time: time = Field(..., description="End time of work day (e.g., 17:00)")
    work_hours_per_day: int = Field(8, ge=1, le=24, description="Total working hours per day")
    
    # Week configuration
    monday_enabled: bool = True
    tuesday_enabled: bool = True
    wednesday_enabled: bool = True
    thursday_enabled: bool = False  # Holiday in Iran
    friday_enabled: bool = False    # Holiday in Iran
    saturday_enabled: bool = True
    sunday_enabled: bool = True
    
    # Break times (optional)
    break_start_time: Optional[time] = Field(None, description="Lunch break start time")
    break_end_time: Optional[time] = Field(None, description="Lunch break end time")
    break_duration_minutes: int = Field(60, ge=0, le=480, description="Break duration in minutes")
    
    timezone: str = Field("Asia/Tehran", description="User timezone")
    effective_from: date = Field(..., description="When this schedule becomes effective")
    effective_to: Optional[date] = Field(None, description="When this schedule expires")
    notes: Optional[str] = Field(None, max_length=1000)

    @model_validator(mode="after")
    def check_time_ranges(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if (self.break_start_time and self.break_end_time) and not (self.start_time < self.break_start_time < self.break_end_time < self.end_time):
            raise ValueError("Break times must be within working hours and start before end")
        # Strip tzinfo & microseconds
        self.start_time = self.start_time.replace(tzinfo=None, microsecond=0)
        self.end_time = self.end_time.replace(tzinfo=None, microsecond=0)
        if self.break_start_time:
            self.break_start_time = self.break_start_time.replace(tzinfo=None, microsecond=0)
        if self.break_end_time:
            self.break_end_time = self.break_end_time.replace(tzinfo=None, microsecond=0)
        return self

    # strip timezone & microseconds for MySQL TIME compatibility
    @field_validator('start_time', 'end_time', 'break_start_time', 'break_end_time', mode='before')
    def _strip_tz(cls, v):
        if isinstance(v, time):
            return v.replace(tzinfo=None, microsecond=0)
        return v

class WorkingHoursCreate(WorkingHoursBase):
    user_id: int

class WorkingHoursUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    work_hours_per_day: Optional[int] = Field(None, ge=1, le=24)
    
    monday_enabled: Optional[bool] = None
    tuesday_enabled: Optional[bool] = None
    wednesday_enabled: Optional[bool] = None
    thursday_enabled: Optional[bool] = None
    friday_enabled: Optional[bool] = None
    saturday_enabled: Optional[bool] = None
    sunday_enabled: Optional[bool] = None
    
    break_start_time: Optional[time] = None
    break_end_time: Optional[time] = None
    break_duration_minutes: Optional[int] = Field(None, ge=0, le=480)
    
    timezone: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    notes: Optional[str] = Field(None, max_length=1000)

    # ensure times are naive for DB
    @field_validator('start_time', 'end_time', 'break_start_time', 'break_end_time', mode='before')
    def _strip_tz(cls, v):
        if isinstance(v, time):
            return v.replace(tzinfo=None, microsecond=0)
        return v

    @model_validator(mode="after")
    def check_time_ranges(self):
        # sanitize provided times
        if self.start_time:
            self.start_time = self.start_time.replace(tzinfo=None, microsecond=0)
        if self.end_time:
            self.end_time = self.end_time.replace(tzinfo=None, microsecond=0)
        if self.break_start_time:
            self.break_start_time = self.break_start_time.replace(tzinfo=None, microsecond=0)
        if self.break_end_time:
            self.break_end_time = self.break_end_time.replace(tzinfo=None, microsecond=0)
        return self

class WorkingHoursResponse(WorkingHoursBase):
    id: int
    user_id: int
    set_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    user_name: Optional[str] = None
    user_full_name: Optional[str] = None
    set_by_name: Optional[str] = None

    class Config:
        from_attributes = True

class WorkingHoursSummary(BaseModel):
    """Summary of working hours for dashboard/reports"""
    user_id: int
    user_name: str
    user_full_name: str
    current_schedule: Optional[WorkingHoursResponse] = None
    total_hours_per_week: int = 0
    working_days_count: int = 0
    is_holiday_today: bool = False
    next_holiday: Optional[date] = None

# Holiday schemas
class HolidayBase(BaseModel):
    name: str = Field(..., max_length=200)
    date: date
    calendar_type: CalendarType = CalendarType.NATIONAL
    is_national: bool = True
    is_recurring: bool = False
    jalali_year: Optional[int] = Field(None, ge=1300, le=1500)
    jalali_month: Optional[int] = Field(None, ge=1, le=12)
    jalali_day: Optional[int] = Field(None, ge=1, le=31)
    description: Optional[str] = Field(None, max_length=1000)

class HolidayCreate(HolidayBase):
    pass

class HolidayUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    holiday_date: Optional[date] = None
    calendar_type: Optional[CalendarType] = None
    is_national: Optional[bool] = None
    is_recurring: Optional[bool] = None
    jalali_year: Optional[int] = Field(None, ge=1300, le=1500)
    jalali_month: Optional[int] = Field(None, ge=1, le=12)
    jalali_day: Optional[int] = Field(None, ge=1, le=31)
    description: Optional[str] = Field(None, max_length=1000)

class HolidayResponse(HolidayBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    created_by_name: Optional[str] = None

    class Config:
        from_attributes = True

# Time off request schemas
class TimeOffBase(BaseModel):
    start_date: date
    end_date: date
    reason: Optional[str] = Field(None, max_length=500)

class TimeOffCreate(TimeOffBase):
    user_id: Optional[int] = None

class TimeOffUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, max_length=500)
    status: Optional[TimeOffStatus] = None
    approval_notes: Optional[str] = Field(None, max_length=1000)

class TimeOffResponse(TimeOffBase):
    id: int
    user_id: int
    status: TimeOffStatus
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields
    user_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    days_count: Optional[int] = None

    class Config:
        from_attributes = True

# Bulk operations
class BulkHolidayCreate(BaseModel):
    holidays: List[HolidayCreate]

class WorkingDayCheck(BaseModel):
    """Check if a specific date is a working day for a user"""
    user_id: int
    date: date
    is_working_day: bool
    is_holiday: bool
    is_time_off: bool
    holiday_name: Optional[str] = None
    working_hours: Optional[WorkingHoursResponse] = None

class UserWorkSchedule(BaseModel):
    """Complete work schedule for a user including holidays and time off"""
    user_id: int
    user_name: str
    current_working_hours: Optional[WorkingHoursResponse] = None
    upcoming_holidays: List[HolidayResponse] = []
    pending_time_off: List[TimeOffResponse] = []
    approved_time_off: List[TimeOffResponse] = []

# Daily calendar output
class WorkDayStatus(BaseModel):
    date: date
    is_working_day: bool
    is_holiday: bool
    is_time_off: bool
    holiday_name: Optional[str] = None
    time_off_id: Optional[int] = None
