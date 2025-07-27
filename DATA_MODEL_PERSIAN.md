# 📊 مدل داده‌های سیستم مدیریت تسک گینگا تک

## 📋 فهرست مطالب
- [بررسی کلی](#بررسی-کلی)
- [نقش‌ها و سطوح دسترسی](#نقش‌ها-و-سطوح-دسترسی)
- [مدل‌های اصلی](#مدل‌های-اصلی)
- [روابط بین مدل‌ها](#روابط-بین-مدل‌ها)
- [نمودار ERD](#نمودار-erd)
- [توضیحات تکمیلی](#توضیحات-تکمیلی)

---

## 🎯 بررسی کلی

سیستم مدیریت تسک گینگا تک شامل **11 مدل اصلی** می‌باشد که برای پیاده‌سازی یک سیستم جامع مدیریت پروژه و تسک با قابلیت‌های چابک (Agile) طراحی شده است.

### ویژگی‌های کلیدی سیستم:
- 🔐 **احراز هویت و مجوزها**: مبتنی بر JWT و نقش‌محور
- 👥 **مدیریت تیم**: ساختار سلسله‌مراتبی با رهبر تیم
- 📊 **مدیریت پروژه**: چرخه کامل پروژه از شروع تا اتمام
- ⚡ **چابک‌سازی**: اسپرینت، بک‌لاگ، و نقاط داستان
- 📈 **گزارش‌دهی**: تحلیل زمان، بهره‌وری، و پیشرفت
- 🐛 **ردیابی باگ**: سیستم جامع گزارش مشکلات

---

## 🔐 نقش‌ها و سطوح دسترسی

### تعریف نقش‌ها (UserRole)
```python
class UserRole(enum.Enum):
    ADMIN = "admin"                    # 👨‍💼 مدیر سیستم
    PROJECT_MANAGER = "project_manager" # 📋 مدیر پروژه  
    TEAM_LEADER = "team_leader"        # 👨‍💻 رهبر تیم
    DEVELOPER = "developer"            # 💻 توسعه‌دهنده
    TESTER = "tester"                 # 🧪 تست‌کننده
    VIEWER = "viewer"                 # 👁️ مشاهده‌گر
```

### ماتریس دسترسی‌ها

| نقش | ایجاد پروژه | مدیریت تیم | ایجاد تسک | مشاهده گزارش | لاگ زمان |
|-----|------------|------------|------------|---------------|----------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Project Manager** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Team Leader** | ❌ | در پروژه‌های تعین شده | ✅ | ✅ | ✅ |
| **Developer** | ❌ | ❌ | فقط تسک‌های شخصی | محدود | ✅ |
| **Tester** | ❌ | ❌ | فقط تسک‌های شخصی | محدود | ✅ |
| **Viewer** | ❌ | ❌ | ❌ | مشاهده فقط | ❌ |

---

## 📊 مدل‌های اصلی

### 1️⃣ User (کاربر)
```python
class User(Base):
    __tablename__ = "users"
    
    # فیلدهای اصلی
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(Enum(UserRole), default=UserRole.DEVELOPER)
    is_active = Column(Boolean, default=True)
    
    # تاریخ‌ها
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
```

**توضیحات:**
- 👤 **هویت**: شناسه یکتا، نام کاربری، ایمیل
- 🔒 **امنیت**: رمز عبور هش شده، وضعیت فعال/غیرفعال
- 🎭 **نقش**: تعیین سطح دسترسی کاربر
- 📱 **پروفایل**: نام و نام خانوادگی

---

### 2️⃣ Team (تیم)
```python
class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    team_leader_id = Column(Integer, ForeignKey("users.id"))
    
    # روابط چندگانه
    team_leader = relationship("User", foreign_keys=[team_leader_id])
    members = relationship("User", secondary=team_members)
    projects = relationship("Project", secondary=team_projects)
```

**ویژگی‌های کلیدی:**
- 👨‍💻 **رهبری**: هر تیم یک رهبر دارد
- 👥 **عضویت**: روابط many-to-many با کاربران
- 📋 **پروژه‌ها**: هر تیم می‌تواند در چندین پروژه کار کند

---

### 3️⃣ Project (پروژه)
```python
class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_by_id = Column(Integer, ForeignKey("users.id"))
```

**وضعیت‌های پروژه:**
```python
class ProjectStatus(enum.Enum):
    ACTIVE = "active"        # 🟢 فعال
    COMPLETED = "completed"  # 🔵 تکمیل شده
    ARCHIVED = "archived"    # 🔒 بایگانی شده
```

---

### 4️⃣ Task (تسک)
```python
class Task(Base):
    __tablename__ = "tasks"
    
    # اطلاعات اصلی
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # برنامه‌ریزی و تخمین
    story_points = Column(Integer, default=0)
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    due_date = Column(DateTime(timezone=True))
    
    # روابط
    project_id = Column(Integer, ForeignKey("projects.id"))
    sprint_id = Column(Integer, ForeignKey("sprints.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_by_id = Column(Integer, ForeignKey("users.id"))
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
```

**وضعیت‌های تسک:**
```python
class TaskStatus(enum.Enum):
    TODO = "todo"                # 📝 انجام نشده
    IN_PROGRESS = "in_progress"  # ⚡ در حال انجام
    REVIEW = "review"            # 👀 در حال بررسی
    DONE = "done"               # ✅ انجام شده
    BLOCKED = "blocked"         # 🚫 مسدود شده
```

**اولویت‌های تسک:**
```python
class TaskPriority(enum.IntEnum):
    LOW = 1         # 🟢 کم
    MEDIUM = 2      # 🟡 متوسط
    HIGH = 3        # 🟠 بالا
    CRITICAL = 4    # 🔴 بحرانی
```

---

### 5️⃣ Sprint (اسپرینت)
```python
class Sprint(Base):
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(Enum(SprintStatus), default=SprintStatus.PLANNED)
    project_id = Column(Integer, ForeignKey("projects.id"))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
```

**وضعیت‌های اسپرینت:**
```python
class SprintStatus(enum.Enum):
    PLANNED = "planned"      # 📋 برنامه‌ریزی شده
    ACTIVE = "active"        # ⚡ فعال
    COMPLETED = "completed"  # ✅ تکمیل شده
```

---

### 6️⃣ TimeLog (لاگ زمان)
```python
class TimeLog(Base):
    __tablename__ = "time_logs"
    
    id = Column(Integer, primary_key=True)
    description = Column(Text)
    hours = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # روابط
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
```

**ویژگی‌های کلیدی:**
- ⏱️ **ثبت زمان**: دقیق تا دقیقه
- 📝 **توضیحات**: شرح کار انجام شده
- 🔄 **بروزرسانی خودکار**: actual_hours تسک به‌روزرسانی می‌شود

---

### 7️⃣ Milestone (نقطه عطف)
```python
class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    sprint_id = Column(Integer, ForeignKey("sprints.id"))
    due_date = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
```

**انواع نقاط عطف:**
- 🎯 **پروژه‌ای**: مربوط به کل پروژه
- 🏃‍♂️ **اسپرینت**: مربوط به اسپرینت خاص

---

### 8️⃣ Backlog (بک‌لاگ)
```python
class Backlog(Base):
    __tablename__ = "backlogs"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
```

**کاربرد:**
- 📋 **مخزن ایده‌ها**: ذخیره کردن ایده‌های آینده
- 🔄 **تبدیل به تسک**: امکان تبدیل به تسک فعال

---

### 9️⃣ BugReport (گزارش باگ)
```python
class BugReport(Base):
    __tablename__ = "bug_reports"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    steps_to_reproduce = Column(Text)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text)
    severity = Column(String(20), default="medium")
    status = Column(String(20), default="open")
    
    # روابط
    task_id = Column(Integer, ForeignKey("tasks.id"))
    reported_by_id = Column(Integer, ForeignKey("users.id"))
```

**فیلدهای کلیدی:**
- 🐛 **توضیحات کامل**: مراحل تکرار، رفتار مورد انتظار و واقعی
- 📊 **شدت**: سطح اهمیت باگ
- 🔗 **اتصال به تسک**: ارتباط با تسک مربوطه

---

### 🔟 Tag (برچسب)
```python
class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(7), default="#007bff")
    
    # رابطه many-to-many با تسک‌ها
    tasks = relationship("Task", secondary=task_tags)
```

**کاربردها:**
- 🏷️ **دسته‌بندی**: برچسب‌گذاری تسک‌ها
- 🎨 **رنگ‌بندی**: هر برچسب رنگ مخصوص به خود
- 🔍 **جستجو**: امکان فیلتر کردن بر اساس برچسب

---

### 1️⃣1️⃣ CompletedStoryPoints (امتیازات داستان تکمیل شده)
```python
class CompletedStoryPoints(Base):
    __tablename__ = "completed_story_points"
    
    id = Column(Integer, primary_key=True)
    story_points = Column(Integer, nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    completed_at = Column(DateTime(timezone=True))
```

**هدف:**
- 📈 **تحلیل عملکرد**: ردیابی پیشرفت در اسپرینت
- 👤 **عملکرد فردی**: امتیازات تکمیل شده هر کاربر
- 📊 **گزارش‌دهی**: داده‌های Burndown Chart

---

## 🔗 روابط بین مدل‌ها

### روابط One-to-Many (یک به چند)

#### 👤 User → Relations
- User → Projects (created_by)
- User → Tasks (assignee)
- User → Tasks (created_by) 
- User → TimeLogs
- User → BugReports
- User → Teams (led_teams)

#### 📋 Project → Relations
- Project → Tasks
- Project → Sprints
- Project → Backlogs
- Project → Milestones

#### 🏃‍♂️ Sprint → Relations
- Sprint → Tasks
- Sprint → Milestones

#### 📝 Task → Relations
- Task → Subtasks (self-referencing)
- Task → TimeLogs
- Task → BugReports

### روابط Many-to-Many (چند به چند)

#### 👥 Team Relations
```python
# جدول میانی: team_members
Team ↔ User (members)

# جدول میانی: team_projects  
Team ↔ Project
```

#### 🏷️ Tag Relations
```python
# جدول میانی: task_tags
Task ↔ Tag
```

---

## 📈 نمودار ERD (ساده شده)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    User     │    │    Team     │    │   Project   │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │    │ id (PK)     │    │ id (PK)     │
│ username    │◄──►│ name        │◄──►│ name        │
│ email       │    │ description │    │ description │
│ role        │    │ leader_id   │    │ status      │
│ is_active   │    └─────────────┘    │ start_date  │
└─────────────┘                       │ end_date    │
       │                              └─────────────┘
       │                                     │
       ▼                                     ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Task     │    │   Sprint    │    │  Milestone  │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │◄──►│ id (PK)     │    │ id (PK)     │
│ title       │    │ name        │    │ name        │
│ status      │    │ status      │    │ due_date    │
│ priority    │    │ start_date  │    │ completed   │
│ story_pts   │    │ end_date    │    └─────────────┘
└─────────────┘    └─────────────┘           │
       │                   │                │
       ▼                   ▼                ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   TimeLog   │    │   Backlog   │    │ BugReport   │
├─────────────┤    ├─────────────┤    ├─────────────┤
│ id (PK)     │    │ id (PK)     │    │ id (PK)     │
│ hours       │    │ title       │    │ title       │
│ date        │    │ description │    │ severity    │
│ description │    └─────────────┘    │ status      │
└─────────────┘                       └─────────────┘
```

---

## 🛠️ توضیحات تکمیلی

### 🔄 چرخه حیات پروژه

1. **ایجاد پروژه** → Project Manager یا Admin
2. **تشکیل تیم** → اختصاص تیم به پروژه
3. **برنامه‌ریزی** → ایجاد Backlog و Milestone
4. **اجرا** → ایجاد Sprint و Task
5. **نظارت** → TimeLog و گزارش‌دهی
6. **اتمام** → بستن Sprint و Project

### 📊 سیستم گزارش‌دهی

#### انواع گزارش‌ها:
- **📈 Time Reports**: تحلیل زمان صرف شده
- **🎯 Story Points**: پیشرفت اسپرینت
- **👥 Team Productivity**: عملکرد تیم
- **📋 Project Progress**: وضعیت پروژه
- **🔥 Burndown Chart**: نمودار پیشرفت اسپرینت

### 🔐 سیستم امنیتی

#### لایه‌های امنیت:
1. **Authentication**: JWT Token
2. **Authorization**: Role-based Access
3. **Data Validation**: Pydantic Schemas
4. **Permission Checks**: در هر API endpoint

### 🎯 ویژگی‌های خاص

#### Kanban Board:
- 📊 نمایش visual تسک‌ها
- 🔄 انتقال drag & drop
- 🎨 رنگ‌بندی بر اساس اولویت

#### Time Tracking:
- ⏱️ Timer دستی و خودکار
- 📝 توضیحات دقیق
- 📊 گزارش‌های تفصیلی

#### Agile Support:
- 🏃‍♂️ Sprint management
- 📋 Product/Sprint backlog
- 🎯 Story points tracking
- 📈 Burndown charts

---

## 📝 نتیجه‌گیری

این مدل داده برای پشتیبانی از یک سیستم جامع مدیریت پروژه طراحی شده که:

✅ **انعطاف‌پذیری**: قابلیت تطبیق با روش‌های مختلف پروژه
✅ **مقیاس‌پذیری**: پشتیبانی از تیم‌ها و پروژه‌های بزرگ  
✅ **ردیابی دقیق**: ثبت جزئیات کامل زمان و پیشرفت
✅ **گزارش‌دهی قدرتمند**: تحلیل‌های عمیق عملکرد
✅ **امنیت**: کنترل دسترسی دقیق و امن

این ساختار امکان مدیریت موثر پروژه‌های نرم‌افزاری با رویکرد چابک را فراهم می‌کند.
