"""
Jalali calendar utilities for Iranian holidays and working hours
"""

from datetime import date, timedelta
from typing import List, Optional, Dict, Any
import calendar
import jdatetime
from hijri_converter import Gregorian as HijriGregorian, Hijri


class JalaliCalendar:
    """Jalali (Persian) calendar utilities for Iranian holidays and date conversion"""
    
    MONTH_NAMES = [
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    ]
    
    # Solar (Jalali) fixed-date holidays (official calendar)
    FIXED_SOLAR_HOLIDAYS = {
        # Nowruz holidays (Persian New Year)
        (1, 1): "جشن نوروز - سال نو",
        (1, 2): "دومین روز نوروز",
        (1, 3): "سومین روز نوروز", 
        (1, 4): "چهارمین روز نوروز",
        
        # National holidays
        (3, 14): "رحلت امام خمینی",
        (3, 15): "قیام 15 خرداد",
        (6, 30): "شهادت حضرت علی",
        (11, 22): "پیروزی انقلاب اسلامی",
        (12, 29): "روز ملی شدن صنعت نفت ایران",
    }

    # Lunar (Hijri) variable-date holidays — month index starts at 1 (Muharram)
    LUNAR_HOLIDAYS = {
        (10, 1): "عید فطر",          # 1 Shawwal
        (12, 10): "عید قربان",       # 10 Dhu al-Hijjah
        (12, 18): "عید غدیر",
        (1, 9): "تاسوعا",
        (1, 10): "عاشورا",
        (3, 17): "میلاد حضرت محمد (ص)",
        (7, 27): "بعثت پیامبر اکرم (ص)",
    }
    
    @staticmethod
    def is_leap_year(jalali_year: int) -> bool:
        """Check if a Jalali year is leap year"""
        # Simplified leap year calculation for Jalali calendar
        cycle = jalali_year % 128
        if cycle <= 29:
            return cycle % 33 in [1, 5, 9, 13, 17, 22, 26, 30]
        elif cycle <= 62:
            return (cycle - 29) % 33 in [1, 5, 9, 13, 17, 22, 26, 30]
        elif cycle <= 95:
            return (cycle - 62) % 33 in [1, 5, 9, 13, 17, 22, 26, 30]
        else:
            return (cycle - 95) % 33 in [1, 5, 9, 13, 17, 22, 26, 30]
    
    @staticmethod
    def jalali_to_gregorian(jalali_year: int, jalali_month: int, jalali_day: int) -> date:
        """Convert Jalali date to Gregorian date (approximate conversion)"""
        # This is a simplified conversion - for production use a proper library like jdatetime
        # Approximate conversion for demonstration
        
        # Base year difference (approximate)
        gregorian_year = jalali_year + 621
        
        # Approximate month and day conversion
        if jalali_month <= 6:
            gregorian_month = jalali_month + 3
            gregorian_day = jalali_day
        else:
            gregorian_month = jalali_month - 6
            gregorian_day = jalali_day
            
        # Adjust for year overflow
        if gregorian_month > 12:
            gregorian_month -= 12
            gregorian_year += 1
            
        # Ensure valid day
        max_days = calendar.monthrange(gregorian_year, gregorian_month)[1]
        gregorian_day = min(gregorian_day, max_days)
        
        try:
            return date(gregorian_year, gregorian_month, gregorian_day)
        except ValueError:
            # Fallback to a safe date
            return date(gregorian_year, 1, 1)
    
    @staticmethod
    def gregorian_to_jalali(gregorian_date: date) -> tuple:
        """Convert Gregorian date to Jalali date (approximate conversion)"""
        # This is a simplified conversion - for production use a proper library like jdatetime
        gregorian_year = gregorian_date.year
        gregorian_month = gregorian_date.month
        gregorian_day = gregorian_date.day
        
        # Approximate conversion
        jalali_year = gregorian_year - 621
        
        if gregorian_month >= 3:
            jalali_month = gregorian_month - 3
            jalali_day = gregorian_day
        else:
            jalali_month = gregorian_month + 6
            jalali_day = gregorian_day
            jalali_year -= 1
            
        # Ensure valid ranges
        jalali_month = max(1, min(12, jalali_month))
        jalali_day = max(1, min(31, jalali_day))
        
        return (jalali_year, jalali_month, jalali_day)
    
    @classmethod
    def get_iranian_holidays(cls, year: int, include_weekly: bool = True) -> List[Dict[str, Any]]:
        """Return official Iranian holidays (solar + lunar) for given Gregorian year."""

        holidays: List[Dict[str, Any]] = []

        # 1. Solar fixed holidays – convert from Jalali to Gregorian using jdatetime
        jalali_year = year - 621  # rough mapping; jdatetime handles overflow internally
        for (j_month, j_day), name in cls.FIXED_SOLAR_HOLIDAYS.items():
            try:
                g_date = jdatetime.date(jalali_year, j_month, j_day).togregorian()
                holidays.append({
                    'name': name,
                    'date': g_date,
                    'jalali_year': jalali_year,
                    'jalali_month': j_month,
                    'jalali_day': j_day,
                    'calendar_type': 'national',
                    'is_national': True,
                    'is_recurring': True,
                })
            except (ValueError, OverflowError):
                continue

        # 2. Lunar holidays – iterate all days of the Gregorian year once, map to Hijri and check
        current = date(year, 1, 1)
        end_date = date(year, 12, 31)
        while current <= end_date:
            h_date = HijriGregorian(current.year, current.month, current.day).to_hijri()
            key = (h_date.month, h_date.day)
            if key in cls.LUNAR_HOLIDAYS:
                holidays.append({
                    'name': cls.LUNAR_HOLIDAYS[key],
                    'date': current,
                    'calendar_type': 'religious',
                    'is_national': True,
                    'is_recurring': False,
                })
            current += timedelta(days=1)

        # 3. Weekly holidays (Thursday/Friday) – optional
        if include_weekly:
            current = date(year, 1, 1)
            while current <= end_date:
                if current.weekday() == 3:  # Thursday
                    holidays.append({
                        'name': 'تعطیل هفتگی - پنج‌شنبه',
                        'date': current,
                        'calendar_type': 'weekly',
                        'is_national': False,
                        'is_recurring': True,
                    })
                elif current.weekday() == 4:  # Friday
                    holidays.append({
                        'name': 'تعطیل هفتگی - جمعه',
                        'date': current,
                        'calendar_type': 'weekly',
                        'is_national': False,
                        'is_recurring': True,
                    })
                current += timedelta(days=1)

        # Remove duplicates if any (same date + name)
        unique = {(h['date'], h['name']): h for h in holidays}
        return sorted(unique.values(), key=lambda x: x['date'])
    
    @staticmethod
    def is_working_day(check_date: date, working_hours_config: Optional[Dict] = None) -> bool:
        """Check if a date is a working day based on Iranian work week"""
        weekday = check_date.weekday()
        
        # Default Iranian work week (Saturday to Wednesday)
        if working_hours_config:
            day_enabled = {
                0: working_hours_config.get('monday_enabled', True),     # Monday
                1: working_hours_config.get('tuesday_enabled', True),    # Tuesday
                2: working_hours_config.get('wednesday_enabled', True),  # Wednesday
                3: working_hours_config.get('thursday_enabled', False),  # Thursday (holiday)
                4: working_hours_config.get('friday_enabled', False),    # Friday (holiday)
                5: working_hours_config.get('saturday_enabled', True),   # Saturday
                6: working_hours_config.get('sunday_enabled', True),     # Sunday
            }
            return day_enabled.get(weekday, True)
        else:
            # Default: Thursday and Friday are holidays
            return weekday not in [3, 4]  # Not Thursday or Friday
    
    @classmethod
    def get_next_working_day(cls, start_date: date, working_hours_config: Optional[Dict] = None) -> date:
        """Get the next working day after the given date"""
        current = start_date + timedelta(days=1)
        
        while not cls.is_working_day(current, working_hours_config):
            current += timedelta(days=1)
            # Safety check to prevent infinite loop
            if (current - start_date).days > 14:
                break
                
        return current
    
    @classmethod
    def get_working_days_in_range(cls, start_date: date, end_date: date, 
                                  working_hours_config: Optional[Dict] = None) -> List[date]:
        """Get all working days in a date range"""
        working_days = []
        current = start_date
        
        while current <= end_date:
            if cls.is_working_day(current, working_hours_config):
                working_days.append(current)
            current += timedelta(days=1)
            
        return working_days
    
    @classmethod
    def count_working_days(cls, start_date: date, end_date: date, 
                          working_hours_config: Optional[Dict] = None) -> int:
        """Count working days between two dates"""
        return len(cls.get_working_days_in_range(start_date, end_date, working_hours_config))


def get_default_iranian_holidays_for_year(year: int) -> List[Dict[str, Any]]:
    """Get default Iranian holidays for a specific year"""
    return JalaliCalendar.get_iranian_holidays(year)


def is_iranian_holiday(check_date: date) -> bool:
    """Check if a date is an Iranian holiday"""
    holidays = JalaliCalendar.get_iranian_holidays(check_date.year)
    return any(holiday['date'] == check_date for holiday in holidays)


def get_next_holiday(from_date: date = None) -> Optional[date]:
    """Get the next holiday date"""
    if from_date is None:
        from_date = date.today()
    
    holidays = JalaliCalendar.get_iranian_holidays(from_date.year)
    
    # Find next holiday in current year
    for holiday in holidays:
        if holiday['date'] > from_date:
            return holiday['date']
    
    # If no holidays found in current year, check next year
    next_year_holidays = JalaliCalendar.get_iranian_holidays(from_date.year + 1)
    if next_year_holidays:
        return next_year_holidays[0]['date']
    
    return None
