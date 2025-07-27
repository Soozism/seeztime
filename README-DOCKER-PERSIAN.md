# راهنمای اجرای پروژه Ginga Tek با Docker

این راهنما نحوه اجرای پروژه Ginga Tek Task Management API را با استفاده از Docker و پایگاه داده MySQL توضیح می‌دهد.

## پیش‌نیازها

- Docker و Docker Compose نصب شده باشد
- حداقل ۲ گیگابایت RAM در دسترس باشد
- پورت ۸۰۰۰ در دسترس باشد

## شروع سریع

### گزینه ۱: استفاده از اسکریپت راه‌اندازی (توصیه شده)

```bash
# اجرای اسکریپت
./start-dev.sh
```

### گزینه ۲: دستورات Docker دستی

```bash
# ساخت و راه‌اندازی سرویس‌ها
sudo docker compose up --build -d

# بررسی وضعیت سرویس‌ها
sudo docker compose ps

# مشاهده لاگ‌ها
sudo docker compose logs -f
```

## سرویس‌ها

پیکربندی Docker شامل سرویس‌های زیر است:

### ۱. API گینگا تک (پورت ۸۰۰۰)
- **آدرس**: http://localhost:8000
- **مستندات API**: http://localhost:8000/docs
- **مستندات ReDoc**: http://localhost:8000/redoc

### ۲. پایگاه داده MySQL (فقط داخلی)
- **هاست**: mysql (نام داخلی کانتینر)
- **پورت**: ۳۳۰۶ (فقط داخلی)
- **پایگاه داده**: ginga_tek
- **نام کاربری**: gingatek
- **رمز عبور**: gingatek123
- **رمز عبور root**: root123

## کاربر پیش‌فرض مدیر

پس از اولین راه‌اندازی، یک کاربر مدیر پیش‌فرض ایجاد می‌شود:

- **نام کاربری**: admin
- **رمز عبور**: admin123
- **ایمیل**: admin@gingatek.com
- **نقش**: ADMIN

⚠️ **مهم**: پس از اولین ورود، رمز عبور پیش‌فرض را تغییر دهید!

## دستورات مفید

### مشاهده لاگ‌ها
```bash
# تمام سرویس‌ها
sudo docker compose logs -f

# سرویس خاص
sudo docker compose logs -f ginga-tek-api
sudo docker compose logs -f mysql
```

### توقف سرویس‌ها
```bash
sudo docker compose down
```

### راه‌اندازی مجدد سرویس‌ها
```bash
sudo docker compose restart
```

### دسترسی به پایگاه داده MySQL
```bash
# اتصال به کانتینر MySQL
sudo docker compose exec mysql mysql -u gingatek -p ginga_tek

# یا به عنوان root
sudo docker compose exec mysql mysql -u root -p

# یا از کانتینر API
sudo docker compose exec ginga-tek-api mysql -h mysql -u gingatek -p ginga_tek
```

### اجرای مایگریشن‌های پایگاه داده
```bash
# دسترسی به کانتینر API
sudo docker compose exec ginga-tek-api bash

# اجرای مایگریشن‌ها
alembic upgrade head
```

### ایجاد مایگریشن جدید
```bash
# دسترسی به کانتینر API
sudo docker compose exec ginga-tek-api bash

# ایجاد مایگریشن جدید
alembic revision --autogenerate -m "توضیح تغییرات"
```

## متغیرهای محیطی

متغیرهای محیطی زیر پیکربندی شده‌اند:

| متغیر | مقدار | توضیح |
|-------|-------|-------|
| `DATABASE_URL` | `mysql://gingatek:gingatek123@mysql:3306/ginga_tek` | رشته اتصال پایگاه داده |
| `SECRET_KEY` | `your-secret-key-change-this` | کلید رمز JWT |
| `DEBUG` | `True` | حالت دیباگ |
| `MYSQL_HOST` | `mysql` | نام هاست MySQL |
| `MYSQL_PORT` | `3306` | پورت MySQL |
| `MYSQL_USER` | `gingatek` | نام کاربری MySQL |
| `MYSQL_PASSWORD` | `gingatek123` | رمز عبور MySQL |
| `MYSQL_DATABASE` | `ginga_tek` | نام پایگاه داده MySQL |

## پیکربندی پایگاه داده

### تنظیمات MySQL
- **نسخه**: MySQL 8.0
- **مجموعه کاراکتر**: utf8mb4
- **کولیشن**: utf8mb4_unicode_ci
- **احراز هویت**: mysql_native_password

### تنظیمات Pool اتصال
- **اندازه Pool**: ۱۰
- **حداکثر سرریز**: ۲۰
- **بازیافت Pool**: ۳۰۰ ثانیه
- **پیش‌پینگ Pool**: فعال

## عیب‌یابی

### سرویس راه‌اندازی نمی‌شود
۱. بررسی کنید که Docker در حال اجرا باشد
۲. بررسی کنید که پورت ۸۰۰۰ در دسترس باشد
۳. لاگ‌ها را مشاهده کنید: `sudo docker compose logs`

### مشکلات اتصال پایگاه داده
۱. منتظر آماده شدن MySQL باشید (اسکریپت راه‌اندازی این کار را انجام می‌دهد)
۲. لاگ‌های MySQL را بررسی کنید: `sudo docker compose logs mysql`
۳. بررسی کنید که پایگاه داده وجود دارد: `sudo docker compose exec mysql mysql -u gingatek -p -e "SHOW DATABASES;"`

### API پاسخ نمی‌دهد
۱. لاگ‌های API را بررسی کنید: `sudo docker compose logs ginga-tek-api`
۲. بررسی کنید که کانتینر API در حال اجرا باشد: `sudo docker compose ps`
۳. بررسی کنید که اسکریپت انتظار با موفقیت تکمیل شده باشد

### بازنشانی کامل
```bash
# توقف و حذف تمام کانتینرها، شبکه‌ها و حجم‌ها
sudo docker compose down -v

# حذف تمام تصاویر
sudo docker compose down --rmi all

# شروع مجدد
./start-dev.sh
```

## گردش کار توسعه

۱. **راه‌اندازی محیط**: `./start-dev.sh`
۲. **تغییرات کد** در فایل‌های محلی
۳. **بازسازی کانتینر API**: `sudo docker compose build ginga-tek-api`
۴. **راه‌اندازی مجدد API**: `sudo docker compose restart ginga-tek-api`
۵. **تست تغییرات** در http://localhost:8000/docs

## ملاحظات تولید

برای استقرار در محیط تولید:

۱. تمام رمزهای عبور پیش‌فرض را تغییر دهید
۲. از SECRET_KEY قوی استفاده کنید
۳. DEBUG=False تنظیم کنید
۴. تنظیمات CORS مناسب را پیکربندی کنید
۵. از پایگاه داده MySQL خارجی استفاده کنید
۶. لاگینگ مناسب را تنظیم کنید
۷. SSL/TLS را پیکربندی کنید
۸. از Docker secrets برای داده‌های حساس استفاده کنید

## ساختار فایل

```
ginga_tek/
├── docker-compose.yml          # پیکربندی سرویس‌های Docker
├── Dockerfile                  # تعریف کانتینر API
├── start-dev.sh               # اسکریپت راه‌اندازی توسعه
├── mysql-access.sh            # اسکریپت دسترسی به MySQL
├── scripts/
│   ├── init-mysql.sql         # راه‌اندازی MySQL
│   └── wait-for-mysql.py      # بررسی آمادگی MySQL
├── app/                       # کد برنامه
└── .dockerignore              # استثناهای ساخت Docker
```

## دسترسی به MySQL

برای دسترسی آسان به پایگاه داده MySQL:

```bash
# استفاده از اسکریپت دسترسی
./mysql-access.sh

# یا دستورات مستقیم
sudo docker compose exec mysql mysql -u gingatek -p ginga_tek
sudo docker compose exec mysql mysql -u root -p
```

## تست عملکرد

برای تست عملکرد سیستم:

```bash
# تست اتصال API
curl http://localhost:8000/

# تست مستندات API
curl http://localhost:8000/docs

# تست اتصال MySQL
sudo docker compose exec mysql mysql -u gingatek -pgingatek123 -e "SELECT 1;"
```

## نکات مهم

- **امنیت**: تمام رمزهای عبور پیش‌فرض را تغییر دهید
- **پشتیبان‌گیری**: داده‌های MySQL در volume ذخیره می‌شوند
- **عملکرد**: برای محیط تولید، تنظیمات pool را بهینه کنید
- **مانیتورینگ**: لاگ‌ها را به طور منظم بررسی کنید

---

**🎉 محیط توسعه Ginga Tek شما آماده است!** 