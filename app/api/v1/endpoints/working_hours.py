"""
Working Hours API endpoints
"""

from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import UserRole, TimeOffStatus
from app.models.working_hours import WorkingHours, Holiday, TimeOff
from app.schemas.working_hours import (
    WorkingHoursCreate, WorkingHoursUpdate, WorkingHoursResponse,
    HolidayCreate, HolidayResponse, BulkHolidayCreate,
    TimeOffResponse,
    WorkingDayCheck, UserWorkSchedule
)
from app.core.jalali_utils import get_default_iranian_holidays_for_year

router = APIRouter()

# Permission helper functions
def can_manage_working_hours(user: User) -> bool:
    """Check if user can manage working hours"""
    return user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]

def can_manage_holidays(user: User) -> bool:
    """Check if user can manage holidays"""
    return user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]

def can_view_working_hours(user: User, target_user_id: int) -> bool:
    """Check if user can view working hours"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    if user.role == UserRole.TEAM_LEADER:
        # Team leaders can view their team members' working hours
        # This would need team membership logic
        return True
    return user.id == target_user_id  # Users can view their own


# Working Hours endpoints
@router.get("/working-hours", response_model=List[WorkingHoursResponse])
def get_working_hours(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    active_only: bool = Query(True, description="Show only active schedules"),
    expand: bool = Query(False, description="Include user names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get working hours schedules"""
    query = db.query(WorkingHours)
    
    # Apply filters
    if user_id:
        if not can_view_working_hours(current_user, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this user's working hours"
            )
        query = query.filter(WorkingHours.user_id == user_id)
    elif current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Non-privileged users can only see their own
        query = query.filter(WorkingHours.user_id == current_user.id)
    
    if active_only:
        today = date.today()
        query = query.filter(
            and_(
                WorkingHours.effective_from <= today,
                or_(WorkingHours.effective_to.is_(None), WorkingHours.effective_to >= today)
            )
        )
    
    working_hours = query.order_by(WorkingHours.effective_from.desc()).all()
    
    if expand:
        result = []
        for wh in working_hours:
            wh_dict = WorkingHoursResponse.from_orm(wh).dict()
            wh_dict['user_name'] = wh.user.username
            wh_dict['user_full_name'] = wh.user.full_name
            wh_dict['set_by_name'] = wh.set_by.username
            result.append(WorkingHoursResponse(**wh_dict))
        return result
    
    return [WorkingHoursResponse.from_orm(wh) for wh in working_hours]


@router.post("/working-hours", response_model=WorkingHoursResponse)
def create_working_hours(
    working_hours_data: WorkingHoursCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new working hours schedule"""
    if not can_manage_working_hours(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create working hours"
        )
    
    # Verify target user exists
    target_user = db.query(User).filter(User.id == working_hours_data.user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate time range
    if working_hours_data.start_time >= working_hours_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    
    # Check for overlapping schedules
    overlapping_query = db.query(WorkingHours).filter(
        WorkingHours.user_id == working_hours_data.user_id
    )
    
    # Handle case where new schedule has no end date (effective_to is None)
    if working_hours_data.effective_to is None:
        overlapping_query = overlapping_query.filter(
            or_(
                WorkingHours.effective_to.is_(None),  # Existing schedule also has no end
                WorkingHours.effective_to >= working_hours_data.effective_from  # Existing schedule ends after new starts
            )
        )
    else:
        # New schedule has an end date
        overlapping_query = overlapping_query.filter(
            and_(
                WorkingHours.effective_from <= working_hours_data.effective_to,
                or_(
                    WorkingHours.effective_to.is_(None),  # Existing schedule has no end
                    WorkingHours.effective_to >= working_hours_data.effective_from  # Existing schedule ends after new starts
                )
            )
        )
    
    overlapping = overlapping_query.first()
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping working hours schedule exists"
        )
    
    # Create working hours
    db_working_hours = WorkingHours(
        **working_hours_data.dict(),
        set_by_id=current_user.id
    )
    
    db.add(db_working_hours)
    db.commit()
    db.refresh(db_working_hours)
    
    return WorkingHoursResponse.from_orm(db_working_hours)


@router.get("/working-hours/{working_hours_id}", response_model=WorkingHoursResponse)
def get_working_hours_by_id(
    working_hours_id: int,
    expand: bool = Query(False, description="Include user names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get working hours by ID"""
    working_hours = db.query(WorkingHours).filter(WorkingHours.id == working_hours_id).first()
    if not working_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Working hours not found"
        )
    
    if not can_view_working_hours(current_user, working_hours.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view these working hours"
        )
    
    if expand:
        wh_dict = WorkingHoursResponse.from_orm(working_hours).dict()
        wh_dict['user_name'] = working_hours.user.username
        wh_dict['user_full_name'] = working_hours.user.full_name
        wh_dict['set_by_name'] = working_hours.set_by.username
        return WorkingHoursResponse(**wh_dict)
    
    return WorkingHoursResponse.from_orm(working_hours)


@router.put("/working-hours/{working_hours_id}", response_model=WorkingHoursResponse)
def update_working_hours(
    working_hours_id: int,
    working_hours_update: WorkingHoursUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update working hours schedule"""
    if not can_manage_working_hours(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update working hours"
        )
    
    working_hours = db.query(WorkingHours).filter(WorkingHours.id == working_hours_id).first()
    if not working_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Working hours not found"
        )
    
    # Update fields
    for field, value in working_hours_update.dict(exclude_unset=True).items():
        setattr(working_hours, field, value)

    # Validate time range
    if working_hours.start_time >= working_hours.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )

    # Check for overlapping schedules (excluding current)
    overlapping = db.query(WorkingHours).filter(
        WorkingHours.user_id == working_hours.user_id,
        WorkingHours.id != working_hours.id,
        and_(
            WorkingHours.effective_from <= (working_hours.effective_to or working_hours.effective_from),
            or_(WorkingHours.effective_to.is_(None), WorkingHours.effective_to >= working_hours.effective_from)
        )
    ).first()

    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Updated schedule overlaps with an existing one"
        )
    
    db.commit()
    db.refresh(working_hours)
    
    return WorkingHoursResponse.from_orm(working_hours)


@router.delete("/working-hours/{working_hours_id}")
def delete_working_hours(
    working_hours_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete working hours schedule"""
    if not can_manage_working_hours(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete working hours"
        )
    
    working_hours = db.query(WorkingHours).filter(WorkingHours.id == working_hours_id).first()
    if not working_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Working hours not found"
        )
    
    db.delete(working_hours)
    db.commit()
    
    return {"message": "Working hours deleted successfully"}


# Holiday management endpoints
@router.get("/holidays", response_model=List[HolidayResponse])
def get_holidays(
    year: Optional[int] = Query(None, description="Filter by year"),
    is_national: Optional[bool] = Query(None, description="Filter by national holidays"),
    expand: bool = Query(False, description="Include creator names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get holidays"""
    query = db.query(Holiday)
    
    if year:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        query = query.filter(and_(Holiday.date >= start_date, Holiday.date <= end_date))
    
    if is_national is not None:
        query = query.filter(Holiday.is_national == is_national)
    
    holidays = query.order_by(Holiday.date).all()
    
    if expand:
        result = []
        for holiday in holidays:
            holiday_dict = HolidayResponse.from_orm(holiday).dict()
            holiday_dict['created_by_name'] = holiday.created_by.username
            result.append(HolidayResponse(**holiday_dict))
        return result
    
    return [HolidayResponse.from_orm(holiday) for holiday in holidays]


@router.post("/holidays", response_model=HolidayResponse)
def create_holiday(
    holiday_data: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new holiday"""
    if not can_manage_holidays(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create holidays"
        )
    
    # Check for duplicate
    existing = db.query(Holiday).filter(
        and_(Holiday.date == holiday_data.date, Holiday.name == holiday_data.name)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Holiday with this name and date already exists"
        )
    
    db_holiday = Holiday(
        **holiday_data.dict(),
        created_by_id=current_user.id
    )
    
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    
    return HolidayResponse.from_orm(db_holiday)


@router.post("/holidays/bulk", response_model=List[HolidayResponse])
def create_holidays_bulk(
    bulk_data: BulkHolidayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create multiple holidays at once"""
    if not can_manage_holidays(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create holidays"
        )
    
    created_holidays = []
    for holiday_data in bulk_data.holidays:
        # Check for duplicate
        existing = db.query(Holiday).filter(
            and_(Holiday.date == holiday_data.date, Holiday.name == holiday_data.name)
        ).first()
        
        if not existing:
            db_holiday = Holiday(
                **holiday_data.dict(),
                created_by_id=current_user.id
            )
            db.add(db_holiday)
            created_holidays.append(db_holiday)
    
    db.commit()
    
    for holiday in created_holidays:
        db.refresh(holiday)
    
    return [HolidayResponse.from_orm(holiday) for holiday in created_holidays]


@router.post("/holidays/iranian/{year}")
def create_iranian_holidays_for_year(
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create default Iranian holidays for a specific year"""
    if not can_manage_holidays(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create holidays"
        )
    
    if year < 2020 or year > 2030:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be between 2020 and 2030"
        )
    
    holidays_data = get_default_iranian_holidays_for_year(year)
    created_count = 0
    
    for holiday_info in holidays_data:
        # Check if holiday already exists
        existing = db.query(Holiday).filter(
            and_(Holiday.date == holiday_info['date'], Holiday.name == holiday_info['name'])
        ).first()
        
        if not existing:
            db_holiday = Holiday(
                name=holiday_info['name'],
                date=holiday_info['date'],
                calendar_type=holiday_info.get('calendar_type', 'national'),
                is_national=holiday_info.get('is_national', True),
                is_recurring=holiday_info.get('is_recurring', False),
                jalali_year=holiday_info.get('jalali_year'),
                jalali_month=holiday_info.get('jalali_month'),
                jalali_day=holiday_info.get('jalali_day'),
                created_by_id=current_user.id
            )
            db.add(db_holiday)
            created_count += 1
    
    db.commit()
    
    return {"message": f"Created {created_count} Iranian holidays for year {year}"}


@router.delete("/holidays/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete holiday"""
    if not can_manage_holidays(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete holidays"
        )
    
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )
    
    db.delete(holiday)
    db.commit()
    
    return {"message": "Holiday deleted successfully"}


# Utility endpoints
@router.get("/check-working-day", response_model=WorkingDayCheck)
def check_working_day(
    user_id: int,
    check_date: date = Query(..., description="Date to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Check if a specific date is a working day for a user"""
    if not can_view_working_hours(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to check this user's working schedule"
        )
    
    # Get user's working hours for the date
    working_hours = db.query(WorkingHours).filter(
        and_(
            WorkingHours.user_id == user_id,
            WorkingHours.effective_from <= check_date,
            or_(WorkingHours.effective_to.is_(None), WorkingHours.effective_to >= check_date)
        )
    ).first()
    
    # Check if it's a holiday
    holiday = db.query(Holiday).filter(Holiday.date == check_date).first()
    
    # Check if user has time off
    time_off = db.query(TimeOff).filter(
        and_(
            TimeOff.user_id == user_id,
            TimeOff.start_date <= check_date,
            TimeOff.end_date >= check_date,
            TimeOff.status == TimeOffStatus.APPROVED
        )
    ).first()
    
    is_holiday = holiday is not None
    is_time_off = time_off is not None
    
    # Check working day based on working hours config
    is_working_day = False
    if working_hours and not is_holiday and not is_time_off:
        weekday = check_date.weekday()
        day_enabled = {
            0: working_hours.monday_enabled,
            1: working_hours.tuesday_enabled,
            2: working_hours.wednesday_enabled,
            3: working_hours.thursday_enabled,
            4: working_hours.friday_enabled,
            5: working_hours.saturday_enabled,
            6: working_hours.sunday_enabled,
        }
        is_working_day = day_enabled.get(weekday, False)
    
    return WorkingDayCheck(
        user_id=user_id,
        date=check_date,
        is_working_day=is_working_day,
        is_holiday=is_holiday,
        is_time_off=is_time_off,
        holiday_name=holiday.name if holiday else None,
        working_hours=WorkingHoursResponse.from_orm(working_hours) if working_hours else None
    )


@router.get("/users/{user_id}/schedule", response_model=UserWorkSchedule)
def get_user_work_schedule(
    user_id: int,
    days_ahead: int = Query(30, ge=1, le=365, description="Days to look ahead for holidays/time off"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get complete work schedule for a user"""
    if not can_view_working_hours(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user's schedule"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    today = date.today()
    future_date = today + timedelta(days=days_ahead)
    
    # Get current working hours
    current_working_hours = db.query(WorkingHours).filter(
        and_(
            WorkingHours.user_id == user_id,
            WorkingHours.effective_from <= today,
            or_(WorkingHours.effective_to.is_(None), WorkingHours.effective_to >= today)
        )
    ).first()
    
    # Get upcoming holidays
    upcoming_holidays = db.query(Holiday).filter(
        and_(Holiday.date >= today, Holiday.date <= future_date)
    ).order_by(Holiday.date).all()
    
    # Get time off requests
    pending_time_off = db.query(TimeOff).filter(
        and_(
            TimeOff.user_id == user_id,
            TimeOff.end_date >= today,
            TimeOff.status == TimeOffStatus.PENDING
        )
    ).order_by(TimeOff.start_date).all()
    
    approved_time_off = db.query(TimeOff).filter(
        and_(
            TimeOff.user_id == user_id,
            TimeOff.end_date >= today,
            TimeOff.status == TimeOffStatus.APPROVED
        )
    ).order_by(TimeOff.start_date).all()
    
    return UserWorkSchedule(
        user_id=user_id,
        user_name=user.username,
        current_working_hours=WorkingHoursResponse.from_orm(current_working_hours) if current_working_hours else None,
        upcoming_holidays=[HolidayResponse.from_orm(h) for h in upcoming_holidays],
        pending_time_off=[TimeOffResponse.from_orm(t) for t in pending_time_off],
        approved_time_off=[TimeOffResponse.from_orm(t) for t in approved_time_off]
    )


# New daily schedule endpoint
from app.schemas.working_hours import WorkDayStatus


@router.get("/working-hours/daily-schedule", response_model=List[WorkDayStatus])
def get_daily_schedule(
    user_id: int = Query(..., description="Target user ID"),
    start_date: date = Query(..., description="Start date of range"),
    end_date: date = Query(..., description="End date of range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Return day-by-day working/holiday/time-off status for a user in given range."""

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must not be after end_date")

    if not can_view_working_hours(current_user, user_id):
        raise HTTPException(status_code=403, detail="Not enough permissions to view schedule")

    # Pre-fetch holidays in range
    holidays = {h.date: h for h in db.query(Holiday).filter(Holiday.date.between(start_date, end_date)).all()}

    # Pre-fetch approved time-off in range
    time_offs = db.query(TimeOff).filter(
        TimeOff.user_id == user_id,
        TimeOff.status == TimeOffStatus.APPROVED,
        TimeOff.end_date >= start_date,
        TimeOff.start_date <= end_date
    ).all()

    time_off_map = {}
    for to in time_offs:
        cur = to.start_date
        while cur <= to.end_date:
            time_off_map[cur] = to.id
            cur += timedelta(days=1)

    # Get working_hours effective schedules for range (simplified: choose config per date)
    schedules = db.query(WorkingHours).filter(
        WorkingHours.user_id == user_id,
        WorkingHours.effective_from <= end_date,
        or_(WorkingHours.effective_to.is_(None), WorkingHours.effective_to >= start_date)
    ).all()

    # Build date loop
    results: List[WorkDayStatus] = []
    cur_day = start_date
    while cur_day <= end_date:
        # Identify applicable schedule (closest effective_from <= cur_day)
        applicable = None
        for sch in schedules:
            if sch.effective_from <= cur_day and (sch.effective_to is None or sch.effective_to >= cur_day):
                if (not applicable) or (sch.effective_from > applicable.effective_from):
                    applicable = sch
        working_day_flag = False
        if applicable:
            weekday = cur_day.weekday()
            day_enabled = {
                0: applicable.monday_enabled,
                1: applicable.tuesday_enabled,
                2: applicable.wednesday_enabled,
                3: applicable.thursday_enabled,
                4: applicable.friday_enabled,
                5: applicable.saturday_enabled,
                6: applicable.sunday_enabled,
            }
            working_day_flag = day_enabled.get(weekday, False)

        is_hol = cur_day in holidays
        is_to = cur_day in time_off_map

        results.append(WorkDayStatus(
            date=cur_day,
            is_working_day=working_day_flag and not is_hol and not is_to,
            is_holiday=is_hol,
            is_time_off=is_to,
            holiday_name=holidays[cur_day].name if is_hol else None,
            time_off_id=time_off_map.get(cur_day)
        ))

        cur_day += timedelta(days=1)

    return results


# Work calendar endpoint per user (alias)

@router.get("/users/{user_id}/work-calendar", response_model=List[WorkDayStatus])
def get_user_work_calendar(
    user_id: int,
    start_date: date = Query(..., description="Start date of range"),
    end_date: date = Query(..., description="End date of range"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Alias to daily schedule endpoint that fits REST pattern under user resource."""

    return get_daily_schedule(  # type: ignore
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        db=db,
        current_user=current_user,
    )
