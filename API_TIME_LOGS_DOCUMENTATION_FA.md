# مستندات کامل API ثبت زمان (Time Logs)

این API برای مدیریت ثبت زمان فعالیت‌ها و تایمرهای زنده در پروژه‌ها استفاده می‌شود و شامل امکانات پیشرفته برای گزارش‌گیری و کنترل دسترسی است.

---

## آدرس‌ها و جزئیات کامل

### ۱. دریافت لیست ثبت زمان‌ها
`GET /api/v1/time_logs/`

**پارامترهای ورودی:**
- `skip` (عدد): شروع صفحه‌بندی (مثال: 0)
- `limit` (عدد): تعداد آیتم‌ها در هر صفحه (مثال: 100)
- `task_id` (عدد): شناسه تسک جهت فیلتر
- `user_id` (عدد): شناسه کاربر جهت فیلتر
- `start_date` (تاریخ): فیلتر از تاریخ (مثال: 2025-07-01T00:00:00)
- `end_date` (تاریخ): فیلتر تا تاریخ (مثال: 2025-07-31T23:59:59)

**نمونه پاسخ:**
```json
[
  {
    "id": 1,
    "task_id": 5,
    "user_id": 2,
    "date": "2025-07-24T09:10:02",
    "hours": 2.5,
    "description": "رفع باگ و تست نهایی",
    "created_at": "2025-07-24T09:10:02",
    "updated_at": null
  },
  ...
]
```

---

### ۲. دریافت تایمر فعال کاربر
`GET /api/v1/time_logs/active-timer`

**پاسخ:**
```json
{
  "id": 3,
  "task_id": 5,
  "user_id": 2,
  "start_time": "2025-07-24T09:00:00",
  "is_active": true,
  "created_at": "2025-07-24T09:00:00",
  "updated_at": null,
  "task_title": "رفع باگ نهایی",
  "task_description": "توضیحات تسک",
  "project_name": "پروژه فروشگاه آنلاین",
  "elapsed_seconds": 600
}
```

---

### ۳. دریافت یک ثبت زمان خاص
`GET /api/v1/time_logs/{time_log_id}`

**پارامتر مسیر:**
- `time_log_id` (عدد): شناسه ثبت زمان

**پاسخ:**
```json
{
  "id": 1,
  "task_id": 5,
  "user_id": 2,
  "date": "2025-07-24T09:10:02",
  "hours": 2.5,
  "description": "رفع باگ و تست نهایی",
  "created_at": "2025-07-24T09:10:02",
  "updated_at": null
}
```

---

### ۴. ثبت زمان جدید
`POST /api/v1/time_logs/`

**بدنه:**
```json
{
  "task_id": 5,
  "hours": 1.5,
  "description": "جلسه برنامه‌ریزی",
  "date": "2025-07-24T08:00:00"
}
```

**پاسخ:**
```json
{
  "id": 2,
  "task_id": 5,
  "user_id": 2,
  "date": "2025-07-24T08:00:00",
  "hours": 1.5,
  "description": "جلسه برنامه‌ریزی",
  "created_at": "2025-07-24T08:00:00",
  "updated_at": null
}
```

---

### ۵. ویرایش ثبت زمان
`PUT /api/v1/time_logs/{time_log_id}`

**پارامتر مسیر:**
- `time_log_id` (عدد): شناسه ثبت زمان

**بدنه:**
```json
{
  "hours": 2.0,
  "description": "ویرایش توضیحات"
}
```

**پاسخ:**
```json
{
  "id": 2,
  "task_id": 5,
  "user_id": 2,
  "date": "2025-07-24T08:00:00",
  "hours": 2.0,
  "description": "ویرایش توضیحات",
  "created_at": "2025-07-24T08:00:00",
  "updated_at": "2025-07-24T10:00:00"
}
```

---

### ۶. حذف ثبت زمان
`DELETE /api/v1/time_logs/{time_log_id}`

**پارامتر مسیر:**
- `time_log_id` (عدد): شناسه ثبت زمان

**پاسخ:**
```json
{ "message": "Time log deleted successfully" }
```

---

### ۷. دریافت ثبت زمان‌های یک تسک
`GET /api/v1/time_logs/task/{task_id}`

**پارامتر مسیر:**
- `task_id` (عدد): شناسه تسک

**پاسخ:**
لیست ثبت زمان‌های مربوط به تسک (`TimeLogResponse`).

---

### ۸. ثبت زمان با پارامترهای پیشرفته
`POST /api/v1/time_logs/log-time`

**پارامترها:**
- `task_id` (عدد): شناسه تسک
- `duration_minutes` (عدد): مدت زمان به دقیقه
- `description` (رشته): توضیحات
- `is_manual` (بولین): ثبت دستی
- `log_date` (تاریخ): تاریخ ثبت

**پاسخ:**
```json
{
  "id": 3,
  "task_id": 5,
  "user_id": 2,
  "date": "2025-07-24T11:00:00",
  "hours": 0.5,
  "description": "ثبت دستی زمان",
  "created_at": "2025-07-24T11:00:00",
  "updated_at": null
}
```

---

### ۹. شروع تایمر زنده
`POST /api/v1/time_logs/start-timer`

**پارامترها:**
- `task_id` (عدد): شناسه تسک

**پاسخ:**
```json
{
  "message": "Timer started successfully",
  "timer_id": 4,
  "task_id": 5,
  "task_title": "رفع باگ نهایی",
  "start_time": "2025-07-24T12:00:00"
}
```

---

### ۱۰. توقف تایمر زنده و ثبت زمان
`POST /api/v1/time_logs/stop-timer`

**پارامترها:**
- `timer_id` (عدد): شناسه تایمر (اختیاری)
- `description` (رشته): توضیحات ثبت زمان

**پاسخ:**
```json
{
  "message": "Timer stopped and time logged successfully",
  "timer_id": 4,
  "elapsed_hours": 1.25,
  "elapsed_seconds": 4500,
  "time_log_id": 5
}
```

---

### ۱۱. دریافت ثبت زمان‌های کاربر جاری
`GET /api/v1/time_logs/user/me`

**پارامترها:**
- `skip` (عدد): شروع صفحه‌بندی
- `limit` (عدد): تعداد آیتم‌ها

**پاسخ:**
لیست ثبت زمان‌های کاربر (`TimeLogResponse`).

---

## مدل‌های پاسخ

### TimeLogResponse
```json
{
  "id": 1,
  "task_id": 5,
  "user_id": 2,
  "date": "2025-07-24T09:10:02",
  "hours": 2.5,
  "description": "رفع باگ و تست نهایی",
  "created_at": "2025-07-24T09:10:02",
  "updated_at": null
}
```

### ActiveTimerResponse
```json
{
  "id": 3,
  "task_id": 5,
  "user_id": 2,
  "start_time": "2025-07-24T09:00:00",
  "is_active": true,
  "created_at": "2025-07-24T09:00:00",
  "updated_at": null,
  "task_title": "رفع باگ نهایی",
  "task_description": "توضیحات تسک",
  "project_name": "پروژه فروشگاه آنلاین",
  "elapsed_seconds": 600
}
```

### TimerStartResponse
```json
{
  "message": "Timer started successfully",
  "timer_id": 4,
  "task_id": 5,
  "task_title": "رفع باگ نهایی",
  "start_time": "2025-07-24T12:00:00"
}
```

### TimerStopResponse
```json
{
  "message": "Timer stopped and time logged successfully",
  "timer_id": 4,
  "elapsed_hours": 1.25,
  "elapsed_seconds": 4500,
  "time_log_id": 5
}
```

---

## نکات و رفتارها
- فقط مدیر یا صاحب ثبت زمان می‌تواند ثبت زمان را ویرایش یا حذف کند.
- توسعه‌دهنده فقط برای تسک‌های خود می‌تواند زمان ثبت کند.
- ثبت‌های تکراری (همان کاربر، همان تسک، همان مدت زمان در ۱۰ ثانیه اخیر) جلوگیری می‌شود.
- ثبت زمان باعث بروزرسانی `actual_hours` تسک می‌شود.
- تایمر زنده فقط برای تسک‌های اختصاص داده‌شده قابل شروع است (مگر مدیر/مدیر پروژه).
