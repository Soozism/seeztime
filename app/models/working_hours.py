"""
Working Hours model for user schedule management
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Time, Boolean, Date, Text, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.enums import TimeOffStatus, CalendarType

class WorkingHours(Base):
    __tablename__ = "working_hours"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Daily working hours
    start_time = Column(Time, nullable=False)  # Start of work day (e.g., 09:00)
    end_time = Column(Time, nullable=False)    # End of work day (e.g., 17:00)
    work_hours_per_day = Column(Integer, nullable=False, default=8)  # Total working hours in a day
    
    # Week configuration
    monday_enabled = Column(Boolean, default=True)
    tuesday_enabled = Column(Boolean, default=True)
    wednesday_enabled = Column(Boolean, default=True)
    thursday_enabled = Column(Boolean, default=False)  # Holiday in Iran
    friday_enabled = Column(Boolean, default=False)    # Holiday in Iran
    saturday_enabled = Column(Boolean, default=True)
    sunday_enabled = Column(Boolean, default=True)
    
    # Break times (optional)
    break_start_time = Column(Time, nullable=True)  # Lunch break start
    break_end_time = Column(Time, nullable=True)    # Lunch break end
    break_duration_minutes = Column(Integer, default=60)  # Break duration in minutes
    
    # Timezone
    timezone = Column(String(50), default="Asia/Tehran")
    
    # Who set this schedule and when
    set_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    effective_from = Column(Date, nullable=False, default=func.current_date())
    effective_to = Column(Date, nullable=True)  # Optional end date
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="working_hours")
    set_by = relationship("User", foreign_keys=[set_by_id])

    def __repr__(self):
        return f"<WorkingHours {self.user.username}: {self.start_time}-{self.end_time}>"


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False)
    calendar_type = Column(SAEnum(CalendarType, name="calendar_type"), default=CalendarType.NATIONAL)
    is_national = Column(Boolean, default=True)  # Backwards compatibility
    is_recurring = Column(Boolean, default=False)  # Yearly recurring (like Nowruz)
    
    # Jalali calendar support
    jalali_year = Column(Integer, nullable=True)
    jalali_month = Column(Integer, nullable=True) 
    jalali_day = Column(Integer, nullable=True)
    
    description = Column(Text, nullable=True)
    
    # Who added this holiday
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        Index("idx_holiday_unique", "date", "name", unique=True),
    )

    def __repr__(self):
        return f"<Holiday {self.name}: {self.date}>"


# User time off requests
class TimeOff(Base):
    __tablename__ = "time_off"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(String(500), nullable=True)
    
    # Approval workflow
    status = Column(SAEnum(TimeOffStatus, name="time_off_status"),
                   nullable=False,
                   default=TimeOffStatus.PENDING)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="time_off_requests")
    approved_by = relationship("User", foreign_keys=[approved_by_id])

    def __repr__(self):
        return f"<TimeOff {self.user.username}: {self.start_date} to {self.end_date}>"


# Add indexes for better performance
Index("idx_working_hours_user_id", WorkingHours.user_id)
Index("idx_working_hours_effective_from", WorkingHours.effective_from)
Index("idx_working_hours_effective_to", WorkingHours.effective_to)
Index("idx_holiday_date", Holiday.date)
Index("idx_holiday_jalali", Holiday.jalali_year, Holiday.jalali_month, Holiday.jalali_day)
Index("idx_time_off_user_id", TimeOff.user_id)
Index("idx_time_off_dates", TimeOff.start_date, TimeOff.end_date)
Index("idx_time_off_status", TimeOff.status)
