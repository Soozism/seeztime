# Ginga Tek - Task Management REST API

A comprehensive task management system built with FastAPI, providing a complete REST API for project management, task tracking, sprint management, and team collaboration.

## Features

## 🏗️ **Architecture**

### **Core Models**
- **User**: Authentication and role management
- **Team**: Groups of users with leaders and project assignments
- **Project**: Container for tasks, sprints, and milestones
- **Task**: Individual work items with status tracking
- **Sprint**: Time-boxed iterations for agile development
- **Backlog**: Product/sprint backlog items
- **Bug Report**: Issue tracking and management
- **Time Log**: Work time tracking and reporting
- **Milestone**: Project goals and deadlines

### **Role-Based Access Control**
- **Admin**: Full system access
- **Project Manager**: Manage projects, teams, and assignments
- **Team Leader**: Manage team's tasks, sprints, and milestones in assigned projects
- **Developer/Tester**: Work on assigned tasks, log time
- **Viewer**: Read-only access to assigned projects

### **Team System**
- **Team Structure**: Each team has a leader and multiple members
- **Project Assignment**: Teams can be assigned to multiple projects
- **Permission Model**: Team leaders can create tasks, sprints, and milestones in their assigned projects
- **Flexible Membership**: Users can be members of multiple teams

### API Features
- **Authentication**: JWT-based authentication with role-based access control
- **RESTful API**: Complete CRUD operations for all entities
- **Dashboard**: Real-time dashboard with project and task statistics
- **Kanban Board**: Visual task management with drag-and-drop support
- **Reporting**: Detailed project reports with analytics
- **Time Tracking**: Comprehensive time logging and reporting
- **Search & Filtering**: Advanced filtering and search capabilities

## Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ginga_tek
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Initialize the database**
   ```bash
   python scripts/create_admin.py
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- **Interactive API Documentation (Swagger)**: http://localhost:8000/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

### Teams
- `GET /api/v1/teams/` - Get all teams (with role-based filtering)
- `POST /api/v1/teams/` - Create team (Admin/Project Manager only)
- `GET /api/v1/teams/{team_id}` - Get team by ID
- `PUT /api/v1/teams/{team_id}` - Update team
- `DELETE /api/v1/teams/{team_id}` - Delete team (Admin/Project Manager only)
- `POST /api/v1/teams/{team_id}/members` - Add team members
- `DELETE /api/v1/teams/{team_id}/members/{user_id}` - Remove team member
- `POST /api/v1/teams/{team_id}/projects` - Assign team to projects
- `DELETE /api/v1/teams/{team_id}/projects/{project_id}` - Remove team from project

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/` - Get all users (Admin only)
- `POST /api/v1/users/` - Create user (Admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID (Admin only)
- `PUT /api/v1/users/{user_id}` - Update user (Admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (Admin only)

### Projects
- `GET /api/v1/projects/` - Get all projects (with filtering)
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{project_id}` - Get project by ID
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project
- `PATCH /api/v1/projects/{project_id}/close` - Close project
- `PATCH /api/v1/projects/{project_id}/reopen` - Reopen project
- `GET /api/v1/projects/{project_id}/tasks` - Get project tasks
- `GET /api/v1/projects/{project_id}/sprints` - Get project sprints

### Tasks
- `GET /api/v1/tasks/` - Get all tasks (with filters)
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{task_id}` - Get task by ID
- `PUT /api/v1/tasks/{task_id}` - Update task
- `DELETE /api/v1/tasks/{task_id}` - Delete task
- `PATCH /api/v1/tasks/{task_id}/status` - Update task status
- `GET /api/v1/tasks/{task_id}/subtasks` - Get task subtasks
- `POST /api/v1/tasks/{task_id}/subtasks` - Create subtask

### Sprints
- `GET /api/v1/sprints/` - Get all sprints
- `POST /api/v1/sprints/` - Create sprint
- `GET /api/v1/sprints/{sprint_id}` - Get sprint by ID
- `PUT /api/v1/sprints/{sprint_id}` - Update sprint
- `DELETE /api/v1/sprints/{sprint_id}` - Delete sprint
- `PATCH /api/v1/sprints/{sprint_id}/close` - Close sprint
- `PATCH /api/v1/sprints/{sprint_id}/reopen` - Reopen sprint
- `POST /api/v1/sprints/{sprint_id}/milestones` - Create sprint milestone

### Backlogs
- `GET /api/v1/backlogs/` - Get all backlogs
- `POST /api/v1/backlogs/` - Create backlog item
- `GET /api/v1/backlogs/{backlog_id}` - Get backlog by ID
- `PUT /api/v1/backlogs/{backlog_id}` - Update backlog
- `DELETE /api/v1/backlogs/{backlog_id}` - Delete backlog
- `POST /api/v1/backlogs/{backlog_id}/convert-to-task` - Convert to task (enhanced)

### Bug Reports
- `GET /api/v1/bug-reports/` - Get all bug reports (with filters)
- `POST /api/v1/bug-reports/` - Create bug report
- `GET /api/v1/bug-reports/{bug_report_id}` - Get bug report by ID
- `PUT /api/v1/bug-reports/{bug_report_id}` - Update bug report
- `DELETE /api/v1/bug-reports/{bug_report_id}` - Delete bug report
- `POST /api/v1/bug-reports/report-problem` - Report task-specific problem
- `POST /api/v1/bug-reports/report-general-problem` - Report general problem
- `POST /api/v1/bug-reports/report-simple-problem` - Report simple problem

### Time Logs
- `GET /api/v1/time-logs/` - Get all time logs (with filters)
- `POST /api/v1/time-logs/` - Create time log
- `POST /api/v1/time-logs/log-time` - Log time with enhanced features
- `POST /api/v1/time-logs/start-timer` - Start timer for task
- `POST /api/v1/time-logs/stop-timer` - Stop active timer
- `GET /api/v1/time-logs/{time_log_id}` - Get time log by ID
- `PUT /api/v1/time-logs/{time_log_id}` - Update time log
- `DELETE /api/v1/time-logs/{time_log_id}` - Delete time log
- `GET /api/v1/time-logs/task/{task_id}` - Get task time logs
- `GET /api/v1/time-logs/user/me` - Get current user's time logs

### Milestones
- `GET /api/v1/milestones/` - Get all milestones (with filters)
- `POST /api/v1/milestones/` - Create milestone
- `GET /api/v1/milestones/{milestone_id}` - Get milestone by ID
- `PUT /api/v1/milestones/{milestone_id}` - Update milestone
- `DELETE /api/v1/milestones/{milestone_id}` - Delete milestone
- `PATCH /api/v1/milestones/{milestone_id}/complete` - Mark milestone complete
- `PATCH /api/v1/milestones/{milestone_id}/reopen` - Reopen milestone

### Bug Reports
- `GET /api/v1/bug-reports/` - Get all bug reports
- `POST /api/v1/bug-reports/` - Create bug report
- `GET /api/v1/bug-reports/{bug_report_id}` - Get bug report by ID
- `PUT /api/v1/bug-reports/{bug_report_id}` - Update bug report
- `DELETE /api/v1/bug-reports/{bug_report_id}` - Delete bug report
- `POST /api/v1/bug-reports/report-problem` - Report problem
- `POST /api/v1/bug-reports/report-general-problem` - Report general problem
- `POST /api/v1/bug-reports/report-simple-problem` - Report simple problem

### Time Logs
- `GET /api/v1/time-logs/` - Get all time logs
- `POST /api/v1/time-logs/` - Create time log
- `GET /api/v1/time-logs/{time_log_id}` - Get time log by ID
- `PUT /api/v1/time-logs/{time_log_id}` - Update time log
- `DELETE /api/v1/time-logs/{time_log_id}` - Delete time log
- `GET /api/v1/time-logs/task/{task_id}` - Get task time logs
- `GET /api/v1/time-logs/user/me` - Get current user's time logs

### Dashboard & Reports
### Reports & Analytics
- `GET /api/v1/reports/time-logs` - Comprehensive time tracking report
- `GET /api/v1/reports/story-points` - Story points completion analysis
- `GET /api/v1/reports/teams` - Team productivity reports
- `GET /api/v1/reports/dashboard` - Executive dashboard summary

### Advanced Analytics
- `GET /api/v1/analytics/productivity-summary` - Productivity metrics by period
- `GET /api/v1/analytics/burndown-chart` - Project/sprint burndown data
- `GET /api/v1/analytics/export/time-logs` - Export time logs (CSV/JSON)
- `GET /api/v1/analytics/workload-analysis` - Team workload and capacity analysis

### Dashboard
- `GET /api/v1/dashboard/` - Main dashboard data
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/reports/project/{project_id}` - Get project report
- `GET /api/v1/kanban/{project_id}` - Get kanban board data

## Project Structure

```
ginga_tek/
├── app/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Application configuration
│   │   ├── database.py        # Database setup and session management
│   │   └── auth.py            # Authentication utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py           # Enumerations
│   │   ├── user.py            # User model
│   │   ├── project.py         # Project model
│   │   ├── task.py            # Task and Subtask models
│   │   ├── sprint.py          # Sprint model
│   │   ├── backlog.py         # Backlog model
│   │   ├── bug_report.py      # Bug Report model
│   │   ├── time_log.py        # Time Log model
│   │   ├── tag.py             # Tag model
│   │   └── completed_sp.py    # Completed Story Points model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # User Pydantic schemas
│   │   ├── project.py         # Project Pydantic schemas
│   │   ├── task.py            # Task Pydantic schemas
│   │   ├── sprint.py          # Sprint Pydantic schemas
│   │   ├── backlog.py         # Backlog Pydantic schemas
│   │   ├── bug_report.py      # Bug Report Pydantic schemas
│   │   └── time_log.py        # Time Log Pydantic schemas
│   └── api/
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py    # API router aggregation
│           └── endpoints/
│               ├── __init__.py
│               ├── auth.py    # Authentication endpoints
│               ├── users.py   # User management endpoints
│               ├── projects.py # Project management endpoints
│               ├── tasks.py   # Task management endpoints
│               ├── sprints.py # Sprint management endpoints
│               ├── backlogs.py # Backlog management endpoints
│               ├── bug_reports.py # Bug report endpoints
│               ├── time_logs.py # Time logging endpoints
│               └── dashboard.py # Dashboard and reporting endpoints
├── scripts/
│   └── create_admin.py        # Create initial admin user
├── main.py                    # FastAPI application entry point
├── migrate.py                 # Database migration script
├── requirements.txt           # Python dependencies
├── alembic.ini               # Alembic configuration
├── .env.example              # Environment variables template
└── README.md                 # This file
```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

```env
# Database Configuration
DATABASE_URL=sqlite:///./ginga_tek.db

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=True
APP_NAME=Ginga Tek Task Management API

# CORS
ALLOWED_HOSTS=["*"]
```

## Database Support

The application supports multiple databases:
- **SQLite** (default): `sqlite:///./ginga_tek.db`
- **PostgreSQL**: `postgresql://username:password@localhost/ginga_tek`
- **MySQL**: `mysql://username:password@localhost/ginga_tek`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints:

1. **Register or login** to get an access token
2. **Include the token** in the Authorization header: `Authorization: Bearer <token>`

## Default Admin User

After running the setup script, you can login with:
- **Username**: admin
- **Password**: admin123
- **Email**: admin@gingatek.com

**⚠️ Important**: Change the default password after first login!

## Features Migrated from Original Project

### Models Converted
✅ All original models have been converted to the new REST API structure:
- User (with role-based access control)
- Project (with status tracking)
- Task (with subtasks, priority, story points)
- Sprint (with status management)
- Backlog (with task conversion)
- Bug Report (with detailed tracking)
- Time Log (with automatic task hour updates)
- Tag (many-to-many with tasks)
- Milestone (project and sprint milestones)
- Completed Story Points (sprint analytics)

### Views Converted to APIs
✅ All original views have been converted to RESTful API endpoints:

**Authentication Views → Auth APIs**
- login → POST /api/v1/auth/login
- logout → Token expiration handling
- register → POST /api/v1/auth/register

**Dashboard Views → Dashboard APIs**
- index → GET /api/v1/dashboard
- dashboard → GET /api/v1/dashboard

**Project Views → Project APIs**
- projects → GET /api/v1/projects/
- project_detail → GET /api/v1/projects/{id}

**Task Views → Task APIs**
- task_detail → GET /api/v1/tasks/{id}

**Kanban Views → Kanban APIs**
- kanban → GET /api/v1/kanban/{project_id}

**Time Entry Views → Time Log APIs**
- time_entry → POST /api/v1/time-logs/

**Reports Views → Report APIs**
- reports → GET /api/v1/reports/project/{id}

**Bug Report Views → Bug Report APIs**
- report_problem → POST /api/v1/bug-reports/report-problem
- report_general_problem → POST /api/v1/bug-reports/report-general-problem

### API Features from Original Project
✅ All original API functionality has been preserved and enhanced:
- Task management (create, edit, get, status updates)
- Project management (create, close, reopen, get sprints/tasks)
- Sprint management (create, edit, close, reopen)
- Backlog management (create, edit, delete, convert to task)
- Bug reporting (multiple report types)
- Milestone management
- Time logging
- Story points tracking

## 📋 **Team Management Workflow**

### **1. Create a Team**
```bash
# Admin/Project Manager creates a team
POST /api/v1/teams/
{
  "name": "Frontend Development Team",
  "description": "Responsible for UI/UX development",
  "team_leader_id": 2,
  "member_ids": [3, 4, 5]
}
```

### **2. Assign Team to Projects**
```bash
# Admin/Project Manager assigns team to projects
POST /api/v1/teams/1/projects
{
  "project_ids": [1, 2]
}
```

### **3. Team Leader Creates Tasks**
```bash
# Team leader creates tasks in assigned projects
POST /api/v1/tasks/
{
  "title": "Implement user dashboard",
  "description": "Create responsive dashboard with charts",
  "project_id": 1,
  "assignee_id": 3,
  "priority": 3
}
```

### **4. Team Leader Creates Sprints**
```bash
# Team leader creates sprints for their projects
POST /api/v1/sprints/
{
  "name": "Sprint 1 - Dashboard MVP",
  "description": "Initial dashboard implementation",
  "project_id": 1,
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-08-04T00:00:00Z"
}
```

### **5. Team Leader Creates Milestones**
```bash
# Team leader sets project milestones
POST /api/v1/milestones/
{
  "name": "Beta Release",
  "description": "Feature complete beta version",
  "project_id": 1,
  "due_date": "2025-08-15T00:00:00Z"
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please create an issue in the repository or contact the development team.
