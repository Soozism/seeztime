# Ginga Tek Task Management API Documentation

## 📋 Overview

The Ginga Tek Task Management API is a comprehensive RESTful API built with FastAPI that provides complete project management functionality including tasks, teams, sprints, bug tracking, time logging, and advanced analytics.

**API Version:** v1  
**Total Endpoints:** 66  
**Base URL:** `http://localhost:8000/api/v1`  
**Documentation:** `http://localhost:8000/docs`  
**Alternative Docs:** `http://localhost:8000/redoc`

## 🚀 New Features & Improvements

### ✅ Enhanced Model Implementations
- **Enum Support**: Bug severity and status now use proper enums
- **Subtask Management**: Tasks support parent-child relationships with `is_subtask` field
- **Updated Timestamps**: All models now include `updated_at` fields
- **Validation Constraints**: Numeric fields have proper validation
- **Performance Indexes**: Database indexes for optimized queries

### ✅ New Models & Endpoints
- **Task Dependencies**: Manage task relationships and dependencies
- **Version Management**: Project versioning and release tracking
- **Task Statistics**: Analytics and progress tracking
- **Translation Support**: Multi-language content management
- **Enhanced Tags**: Tag categorization and management

## 🔐 Authentication

All endpoints (except `/health` and documentation) require authentication using Bearer tokens.

### POST /auth/login
**Description:** Login user and return access token

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Content-Type:** `application/x-www-form-urlencoded`

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### POST /auth/register
**Description:** Register a new user

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "developer",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "developer",
  "is_active": true,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": null
}
```

---

## 👥 Users Management

### GET /users/
**Description:** Get all users (Admin only)

### POST /users/
**Description:** Create a new user (Admin only)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "developer",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 2,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "full_name": "John Doe",
  "role": "developer",
  "is_active": true,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": null
}
```

**Error Responses:**
- `400 Bad Request`: Username or email already exists
- `403 Forbidden`: Not enough permissions (non-admin user)

### GET /users/me/
**Description:** Get current user information

### PUT /users/{user_id}
**Description:** Update user (Admin only or user updating themselves)

### DELETE /users/{user_id}
**Description:** Delete user (Admin only)

### Response Example:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@gingatek.com",
  "first_name": "Admin",
  "last_name": "User",
  "full_name": "Admin User",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-07-21T10:00:00Z",
  "updated_at": "2025-07-21T11:00:00Z"
}
```

---

## 🏢 Teams Management

### POST /teams/
**Description:** Create a new team (Admin/Project Manager only)

**Request Body:**
```json
{
  "name": "Development Team Alpha",
  "description": "Frontend development team",
  "leader_id": 2
}
```

### GET /teams/
**Description:** Get all teams

### PUT /teams/{team_id}
**Description:** Update team

### POST /teams/{team_id}/members
**Description:** Add member to team

**Request Body:**
```json
{
  "user_id": 3
}
```

### DELETE /teams/{team_id}/members/{user_id}
**Description:** Remove member from team

### POST /teams/{team_id}/projects
**Description:** Assign project to team

### DELETE /teams/{team_id}/projects/{project_id}
**Description:** Remove project from team

---

## 📁 Projects Management

### POST /projects/
**Description:** Create a new project

**Request Body:**
```json
{
  "name": "E-commerce Platform",
  "description": "Modern e-commerce solution",
  "status": "active",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z"
}
```

### GET /projects/
**Description:** Get all projects with filtering

**Query Parameters:**
- `skip`: Number of records to skip
- `limit`: Number of records to return
- `status`: Filter by project status

### GET /projects/{project_id}
**Description:** Get project by ID

### PUT /projects/{project_id}
**Description:** Update project

### DELETE /projects/{project_id}
**Description:** Delete project

### POST /projects/{project_id}/close
**Description:** Close project

### POST /projects/{project_id}/reopen
**Description:** Reopen project

### GET /projects/{project_id}/tasks
**Description:** Get all tasks for a project

### GET /projects/{project_id}/sprints
**Description:** Get all sprints for a project

---

## ✅ Tasks Management

### POST /tasks/
**Description:** Create a new task

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Create login and registration functionality",
  "status": "todo",
  "priority": "high",
  "story_points": 8,
  "estimated_hours": 16.0,
  "project_id": 1,
  "sprint_id": 1,
  "assignee_id": 2,
  "is_subtask": false,
  "parent_task_id": null,
  "due_date": "2025-07-28T17:00:00Z"
}
```

### GET /tasks/
**Description:** Get all tasks with filtering

**Query Parameters:**
- `project_id`: Filter by project
- `sprint_id`: Filter by sprint
- `status`: Filter by status
- `assignee_id`: Filter by assignee
- `is_subtask`: Filter subtasks

### GET /tasks/{task_id}
**Description:** Get task by ID

### PUT /tasks/{task_id}
**Description:** Update task

### DELETE /tasks/{task_id}
**Description:** Delete task

### PATCH /tasks/{task_id}/status
**Description:** Update task status

**Request Body:**
```json
{
  "status": "in_progress"
}
```

### GET /tasks/{task_id}/subtasks
**Description:** Get all subtasks of a task

**Response:**
```json
[
  {
    "id": 5,
    "title": "Create login form",
    "status": "todo",
    "priority": "medium",
    "is_subtask": true,
    "parent_task_id": 1,
    "assignee": {
      "id": 2,
      "username": "developer",
      "full_name": "Developer User"
    }
  }
]
```

---

## 📈 Sprints Management

### POST /sprints/
**Description:** Create a new sprint

**Request Body:**
```json
{
  "name": "Sprint 1 - Authentication",
  "description": "Implement user authentication features",
  "project_id": 1,
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-08-04T23:59:59Z",
  "goal": "Complete user authentication system"
}
```

### GET /sprints/
**Description:** Get all sprints

### PUT /sprints/{sprint_id}
**Description:** Update sprint

### DELETE /sprints/{sprint_id}
**Description:** Delete sprint

### POST /sprints/{sprint_id}/close
**Description:** Close sprint

### POST /sprints/{sprint_id}/reopen
**Description:** Reopen sprint

---

## 🎯 Milestones Management

### POST /milestones/
**Description:** Create a new milestone

**Request Body:**
```json
{
  "name": "Beta Release",
  "description": "First beta version ready for testing",
  "project_id": 1,
  "due_date": "2025-09-01T00:00:00Z",
  "sprint_id": 1
}
```

### GET /milestones/
**Description:** Get all milestones

### PUT /milestones/{milestone_id}
**Description:** Update milestone

### PATCH /milestones/{milestone_id}/complete
**Description:** Mark milestone as completed

### PATCH /milestones/{milestone_id}/reopen
**Description:** Reopen completed milestone

---

## ⏱️ Time Logs Management

### POST /time-logs/
**Description:** Create a new time log

**Request Body:**
```json
{
  "task_id": 1,
  "hours": 4.5,
  "description": "Implemented login form validation",
  "date": "2025-07-21"
}
```

### GET /time-logs/
**Description:** Get time logs with filtering

**Query Parameters:**
- `task_id`: Filter by task
- `user_id`: Filter by user
- `date_from`: Start date filter
- `date_to`: End date filter

### POST /time-logs/start-timer
**Description:** Start a time tracking timer

### POST /time-logs/stop-timer
**Description:** Stop time tracking timer

### POST /time-logs/log-time
**Description:** Quick time logging

### GET /time-logs/task/{task_id}
**Description:** Get time logs for a specific task

### GET /time-logs/user/me
**Description:** Get current user's time logs

### PUT /time-logs/{time_log_id}
**Description:** Update time log

### DELETE /time-logs/{time_log_id}
**Description:** Delete time log

---

## 📋 Backlogs Management

### POST /backlogs/
**Description:** Create a new backlog item

**Request Body:**
```json
{
  "title": "User Profile Management",
  "description": "Allow users to manage their profiles",
  "priority": "medium",
  "story_points": 5,
  "project_id": 1
}
```

### GET /backlogs/
**Description:** Get backlog items

### PUT /backlogs/{backlog_id}
**Description:** Update backlog item

### DELETE /backlogs/{backlog_id}
**Description:** Delete backlog item

### POST /backlogs/{backlog_id}/convert-to-task
**Description:** Convert backlog item to task

**Request Body:**
```json
{
  "assignee_id": 2,
  "sprint_id": 1,
  "estimated_hours": 20.0
}
```

---

## 🐛 Bug Reports Management (Enhanced with Enums)

### POST /bug-reports/
**Description:** Create a new bug report

**Request Body:**
```json
{
  "title": "Login button not responsive",
  "description": "The login button doesn't respond to clicks on mobile devices",
  "severity": "high",
  "status": "open",
  "task_id": 1,
  "steps_to_reproduce": "1. Open mobile browser\n2. Navigate to login page\n3. Try clicking login button",
  "expected_behavior": "Button should respond to clicks",
  "actual_behavior": "Button is unresponsive"
}
```

**Bug Severity Enum Values:**
- `critical` - System crashes, data loss
- `high` - Major functionality broken
- `medium` - Minor functionality issues
- `low` - Cosmetic issues, suggestions

**Bug Status Enum Values:**
- `open` - Newly reported
- `in_progress` - Being worked on
- `resolved` - Fixed, awaiting verification
- `closed` - Verified and closed

### GET /bug-reports/
**Description:** Get bug reports with filtering

**Query Parameters:**
- `status`: Filter by status enum
- `severity`: Filter by severity enum
- `assignee_id`: Filter by assignee

### POST /bug-reports/report-simple-problem
**Description:** Quick bug reporting

### POST /bug-reports/report-problem
**Description:** Standard bug reporting

### POST /bug-reports/report-general-problem
**Description:** General issue reporting

### PUT /bug-reports/{bug_report_id}
**Description:** Update bug report

### DELETE /bug-reports/{bug_report_id}
**Description:** Delete bug report

---

## 🔗 Task Dependencies Management (NEW)

### GET /dependencies/task/{task_id}/dependencies
**Description:** Get all dependencies for a task

**Response:**
```json
[
  {
    "id": 1,
    "task_id": 5,
    "depends_on_task_id": 3,
    "dependency_type": "finish_to_start",
    "task": {
      "id": 5,
      "title": "Deploy to production"
    },
    "depends_on_task": {
      "id": 3,
      "title": "Complete testing"
    }
  }
]
```

### POST /dependencies/task/{task_id}/dependencies
**Description:** Create a task dependency

**Request Body:**
```json
{
  "depends_on_task_id": 3,
  "dependency_type": "finish_to_start"
}
```

**Dependency Types:**
- `finish_to_start` - Task must finish before dependent can start
- `start_to_start` - Tasks can start simultaneously
- `finish_to_finish` - Tasks must finish simultaneously
- `start_to_finish` - Dependent task must finish when prerequisite starts

### DELETE /dependencies/task/{task_id}/dependencies/{dependency_id}
**Description:** Remove a task dependency

---

## 📦 Version Management (NEW)

### GET /versions/project/{project_id}/versions
**Description:** Get all versions for a project

**Response:**
```json
[
  {
    "id": 1,
    "project_id": 1,
    "version_number": "1.0.0",
    "description": "Initial release",
    "release_date": "2025-08-01",
    "created_at": "2025-07-21T10:00:00Z",
    "updated_at": null
  }
]
```

### POST /versions/project/{project_id}/versions
**Description:** Create a new version

**Request Body:**
```json
{
  "version_number": "1.1.0",
  "description": "Feature update with user management",
  "release_date": "2025-09-01"
}
```

### PUT /versions/versions/{version_id}
**Description:** Update version

### DELETE /versions/versions/{version_id}
**Description:** Delete version

---

## 🏷️ Tags Management (Enhanced)

### GET /tags/
**Description:** Get all tags with optional category filtering

**Query Parameters:**
- `category`: Filter by tag category

**Response:**
```json
[
  {
    "id": 1,
    "name": "frontend",
    "category": "technology",
    "color": "#3498db",
    "description": "Frontend development related"
  }
]
```

### POST /tags/
**Description:** Create a new tag

**Request Body:**
```json
{
  "name": "urgent",
  "category": "priority",
  "color": "#e74c3c",
  "description": "Urgent priority tasks"
}
```

### GET /tags/categories/
**Description:** Get all tag categories

**Response:**
```json
[
  {
    "category": "technology",
    "count": 5,
    "tags": ["frontend", "backend", "database", "api", "mobile"]
  },
  {
    "category": "priority",
    "count": 3,
    "tags": ["urgent", "normal", "low"]
  }
]
```

### PUT /tags/{tag_id}
**Description:** Update tag

### DELETE /tags/{tag_id}
**Description:** Delete tag

---

## 📊 Dashboard & Analytics

### GET /dashboard/dashboard
**Description:** Get comprehensive dashboard data

**Response:**
```json
{
  "projects": {
    "total": 5,
    "active": 3,
    "completed": 1,
    "on_hold": 1
  },
  "tasks": {
    "total": 25,
    "my_tasks": 8,
    "todo": 3,
    "in_progress": 2,
    "completed": 3,
    "overdue": 1
  },
  "sprints": {
    "active": 2,
    "planned": 1,
    "completed": 4
  },
  "time_logs": {
    "total_hours": 45.5,
    "this_week": 12.5
  },
  "bug_reports": {
    "open": 3,
    "critical": 1,
    "high": 2
  },
  "recent_activities": [
    {
      "type": "task_completed",
      "description": "Task 'Implement user authentication' completed",
      "timestamp": "2025-07-21T14:30:00Z",
      "user": "Developer User"
    }
  ]
}
```

### GET /dashboard/kanban/{project_id}
**Description:** Get kanban board data for a project

**Response:**
```json
{
  "project": {
    "id": 1,
    "name": "E-commerce Platform"
  },
  "columns": {
    "todo": [
      {
        "id": 2,
        "title": "Setup database schema",
        "priority": "medium",
        "story_points": 3,
        "is_subtask": false,
        "assignee": {
          "id": 2,
          "username": "developer",
          "full_name": "Developer User"
        }
      }
    ],
    "in_progress": [...],
    "review": [...],
    "done": [...],
    "blocked": [...]
  }
}
```

### GET /dashboard/reports/project/{project_id}
**Description:** Get detailed project report

---

## 📈 Reports & Analytics

### GET /reports/time-logs
**Description:** Get comprehensive time logs report

**Query Parameters:**
- `date_from`: Start date
- `date_to`: End date
- `user_id`: Filter by user
- `project_id`: Filter by project

### GET /reports/story-points
**Description:** Get story points analysis

### GET /reports/teams
**Description:** Get teams performance report

### GET /reports/dashboard
**Description:** Get executive dashboard report

---

## 🔬 Advanced Analytics

### GET /analytics/productivity-summary
**Description:** Get productivity analytics

**Response:**
```json
{
  "summary": {
    "total_tasks_completed": 28,
    "total_hours_logged": 245.5,
    "average_task_completion_time": 8.77,
    "productivity_score": 82.5,
    "velocity": 15.3
  },
  "team_performance": [
    {
      "team_id": 1,
      "team_name": "Development Team Alpha",
      "tasks_completed": 15,
      "hours_logged": 145.5,
      "velocity": 18,
      "efficiency_score": 85.2
    }
  ]
}
```

### GET /analytics/burndown-chart
**Description:** Get burndown chart data for sprint analysis

**Query Parameters:**
- `sprint_id` (required): Sprint ID
- `project_id`: Project ID

### GET /analytics/workload-analysis
**Description:** Get team and individual workload analysis

### GET /analytics/export/time-logs
**Description:** Export time logs data

**Query Parameters:**
- `format`: Export format (csv, json, excel)
- `date_from`: Start date
- `date_to`: End date

---

## 🏥 Health Check

### GET /health
**Description:** API health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-07-21T16:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## 📝 Data Models & Enums

### User Roles
```json
{
  "admin": "Full system access",
  "project_manager": "Can manage projects and teams", 
  "team_leader": "Can manage team tasks and sprints",
  "developer": "Can work on assigned tasks",
  "tester": "Can test and report bugs",
  "viewer": "Read-only access"
}
```

### Task Status
```json
{
  "todo": "Not started",
  "in_progress": "Currently being worked on",
  "review": "Under review", 
  "done": "Completed",
  "blocked": "Blocked by dependencies"
}
```

### Task Priority
```json
{
  "low": "Low priority",
  "medium": "Medium priority", 
  "high": "High priority",
  "urgent": "Urgent priority"
}
```

### Bug Severity (NEW ENUM)
```json
{
  "critical": "System crashes, data loss",
  "high": "Major functionality broken",
  "medium": "Minor functionality issues", 
  "low": "Cosmetic issues, suggestions"
}
```

### Bug Status (NEW ENUM)
```json
{
  "open": "Newly reported",
  "in_progress": "Being worked on",
  "resolved": "Fixed, awaiting verification",
  "closed": "Verified and closed"
}
```

### Project Status
```json
{
  "active": "Currently active",
  "on_hold": "Temporarily paused",
  "completed": "Finished", 
  "cancelled": "Cancelled"
}
```

---

## 🔧 API Features

### ✅ Enhanced Features
- **Enum Validation**: Proper enum validation for bug severity and status
- **Subtask Support**: Tasks can have parent-child relationships
- **Dependency Management**: Complex task dependency tracking
- **Version Control**: Project versioning and release management
- **Advanced Analytics**: Comprehensive reporting and analytics
- **Tag Categories**: Organized tag management with categories
- **Time Tracking**: Enhanced time logging with timers
- **Team Management**: Complete team workflow management

### 🔒 Security Features
- JWT-based authentication
- Role-based access control (RBAC)
- Permission-based endpoint access
- Data validation and sanitization

### 📊 Performance Features
- Database indexing for optimal queries
- Pagination support for large datasets
- Efficient filtering and search
- Response caching where appropriate

---

## 🚀 Testing the API

### Using Swagger UI
Visit `http://localhost:8000/docs` for interactive API documentation

### Using cURL
```bash
# 1. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"

# 2. Use token in requests
curl -X GET "http://localhost:8000/api/v1/projects/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. Create a new user (Admin only)
curl -X POST "http://localhost:8000/api/v1/users/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "newdev",
       "email": "newdev@example.com",
       "password": "securepassword123",
       "first_name": "John",
       "last_name": "Developer",
       "role": "developer",
       "is_active": true
     }'

# 4. Create a task with subtask support
curl -X POST "http://localhost:8000/api/v1/tasks/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Parent Task",
       "description": "Main task",
       "project_id": 1,
       "is_subtask": false
     }'

# 5. Create a bug report with enums
curl -X POST "http://localhost:8000/api/v1/bug-reports/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Critical Bug",
       "description": "System crash",
       "severity": "critical",
       "status": "open"
     }'
```

---

## 📋 Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized  
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "severity"],
      "msg": "value is not a valid enumeration member; permitted: 'critical', 'high', 'medium', 'low'",
      "type": "type_error.enum"
    }
  ]
}
```

---

## 🎯 Summary

The Ginga Tek Task Management API now provides:

- **66 endpoints** covering all aspects of project management
- **Enhanced data models** with proper enum validation
- **Advanced features** like task dependencies and version management  
- **Comprehensive analytics** and reporting capabilities
- **Modern architecture** with FastAPI and SQLAlchemy
- **Complete documentation** with examples and schemas

This API is production-ready and provides a solid foundation for building comprehensive project management applications.

---

## Teams Management

### POST /teams/
**Description:** Create a new team (Admin/Project Manager only)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Development Team Alpha",
  "description": "Frontend development team",
  "leader_id": 2
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Development Team Alpha",
  "description": "Frontend development team",
  "leader_id": 2,
  "leader": {
    "id": 2,
    "username": "teamlead",
    "full_name": "Team Leader"
  },
  "created_at": "2025-07-21T10:30:00Z",
  "members": [],
  "projects": []
}
```

### GET /teams/
**Description:** Get all teams

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Development Team Alpha",
    "description": "Frontend development team",
    "leader_id": 2,
    "leader": {
      "id": 2,
      "username": "teamlead",
      "full_name": "Team Leader"
    },
    "created_at": "2025-07-21T10:30:00Z",
    "members": [
      {
        "id": 3,
        "username": "developer1",
        "full_name": "Dev One"
      }
    ],
    "projects": [
      {
        "id": 1,
        "name": "Project Alpha",
        "status": "active"
      }
    ]
  }
]
```

### POST /teams/{team_id}/members
**Description:** Add member to team (Admin/Project Manager/Team Leader)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "user_id": 3
}
```

**Response:**
```json
{
  "message": "Member added to team successfully"
}
```

### DELETE /teams/{team_id}/members/{user_id}
**Description:** Remove member from team

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Member removed from team successfully"
}
```

### POST /teams/{team_id}/projects
**Description:** Assign project to team

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "project_id": 1
}
```

**Response:**
```json
{
  "message": "Project assigned to team successfully"
}
```

---

## Projects Management

### POST /projects/
**Description:** Create a new project

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "E-commerce Platform",
  "description": "Modern e-commerce solution",
  "status": "active",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "E-commerce Platform",
  "description": "Modern e-commerce solution",
  "status": "active",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "created_by_id": 1,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": null,
  "created_by": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  }
}
```

### GET /projects/
**Description:** Get all projects (with optional filters)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `skip` (optional): Number of records to skip (default: 0)
- `limit` (optional): Number of records to return (default: 100)
- `status` (optional): Filter by status

**Example:** `GET /projects/?status=active&limit=10`

**Response:**
```json
[
  {
    "id": 1,
    "name": "E-commerce Platform",
    "description": "Modern e-commerce solution",
    "status": "active",
    "start_date": "2025-07-21T00:00:00Z",
    "end_date": "2025-12-31T23:59:59Z",
    "created_by_id": 1,
    "created_at": "2025-07-21T10:30:00Z",
    "created_by": {
      "id": 1,
      "username": "admin",
      "full_name": "Admin User"
    }
  }
]
```

### GET /projects/{project_id}
**Description:** Get project by ID

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "name": "E-commerce Platform",
  "description": "Modern e-commerce solution",
  "status": "active",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "created_by_id": 1,
  "created_at": "2025-07-21T10:30:00Z",
  "created_by": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  },
  "tasks": [],
  "sprints": []
}
```

### PUT /projects/{project_id}
**Description:** Update project

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Updated E-commerce Platform",
  "description": "Updated description",
  "status": "active",
  "end_date": "2026-01-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated E-commerce Platform",
  "description": "Updated description",
  "status": "active",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2026-01-31T23:59:59Z",
  "created_by_id": 1,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": "2025-07-21T11:00:00Z"
}
```

### DELETE /projects/{project_id}
**Description:** Delete project

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Project deleted successfully"
}
```

---

## Tasks Management

### POST /tasks/
**Description:** Create a new task

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Create login and registration functionality",
  "status": "todo",
  "priority": "high",
  "story_points": 8,
  "estimated_hours": 16.0,
  "project_id": 1,
  "sprint_id": 1,
  "assignee_id": 2,
  "due_date": "2025-07-28T17:00:00Z"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Create login and registration functionality",
  "status": "todo",
  "priority": "high",
  "story_points": 8,
  "estimated_hours": 16.0,
  "actual_hours": 0.0,
  "project_id": 1,
  "sprint_id": 1,
  "assignee_id": 2,
  "created_by_id": 1,
  "parent_task_id": null,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": null,
  "due_date": "2025-07-28T17:00:00Z",
  "project": {
    "id": 1,
    "name": "E-commerce Platform"
  },
  "assignee": {
    "id": 2,
    "username": "developer",
    "full_name": "Developer User"
  }
}
```

### GET /tasks/
**Description:** Get all tasks (with optional filters)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `skip` (optional): Number of records to skip
- `limit` (optional): Number of records to return
- `project_id` (optional): Filter by project
- `sprint_id` (optional): Filter by sprint
- `status` (optional): Filter by status
- `assignee_id` (optional): Filter by assignee

**Example:** `GET /tasks/?project_id=1&status=todo`

**Response:**
```json
[
  {
    "id": 1,
    "title": "Implement user authentication",
    "description": "Create login and registration functionality",
    "status": "todo",
    "priority": "high",
    "story_points": 8,
    "estimated_hours": 16.0,
    "actual_hours": 0.0,
    "project_id": 1,
    "assignee_id": 2,
    "created_at": "2025-07-21T10:30:00Z",
    "due_date": "2025-07-28T17:00:00Z"
  }
]
```

### GET /tasks/{task_id}
**Description:** Get task by ID

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "title": "Implement user authentication",
  "description": "Create login and registration functionality",
  "status": "todo",
  "priority": "high",
  "story_points": 8,
  "estimated_hours": 16.0,
  "actual_hours": 0.0,
  "project_id": 1,
  "sprint_id": 1,
  "assignee_id": 2,
  "created_by_id": 1,
  "parent_task_id": null,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": null,
  "due_date": "2025-07-28T17:00:00Z",
  "project": {
    "id": 1,
    "name": "E-commerce Platform"
  },
  "assignee": {
    "id": 2,
    "username": "developer",
    "full_name": "Developer User"
  },
  "subtasks": [],
  "time_logs": []
}
```

### PUT /tasks/{task_id}
**Description:** Update task

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "title": "Updated task title",
  "status": "in_progress",
  "priority": "medium",
  "story_points": 5,
  "estimated_hours": 12.0,
  "actual_hours": 3.0
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Updated task title",
  "description": "Create login and registration functionality",
  "status": "in_progress",
  "priority": "medium",
  "story_points": 5,
  "estimated_hours": 12.0,
  "actual_hours": 3.0,
  "project_id": 1,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": "2025-07-21T11:30:00Z"
}
```

### DELETE /tasks/{task_id}
**Description:** Delete task

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

---

## Sprints Management

### POST /sprints/
**Description:** Create a new sprint (Team Leader only)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Sprint 1 - Authentication",
  "description": "Implement user authentication features",
  "project_id": 1,
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-08-04T23:59:59Z",
  "goal": "Complete user authentication system"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Sprint 1 - Authentication",
  "description": "Implement user authentication features",
  "project_id": 1,
  "status": "planned",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-08-04T23:59:59Z",
  "goal": "Complete user authentication system",
  "created_by_id": 1,
  "created_at": "2025-07-21T10:30:00Z",
  "project": {
    "id": 1,
    "name": "E-commerce Platform"
  },
  "tasks": []
}
```

### GET /sprints/
**Description:** Get all sprints

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `project_id` (optional): Filter by project
- `status` (optional): Filter by status

**Response:**
```json
[
  {
    "id": 1,
    "name": "Sprint 1 - Authentication",
    "description": "Implement user authentication features",
    "project_id": 1,
    "status": "active",
    "start_date": "2025-07-21T00:00:00Z",
    "end_date": "2025-08-04T23:59:59Z",
    "goal": "Complete user authentication system",
    "created_at": "2025-07-21T10:30:00Z"
  }
]
```

### PUT /sprints/{sprint_id}/status
**Description:** Update sprint status

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "status": "active"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Sprint 1 - Authentication",
  "status": "active",
  "start_date": "2025-07-21T00:00:00Z",
  "end_date": "2025-08-04T23:59:59Z",
  "updated_at": "2025-07-21T11:30:00Z"
}
```

---

## Milestones Management

### POST /milestones/
**Description:** Create a new milestone (Team Leader/Project Manager/Admin only)

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Beta Release",
  "description": "First beta version ready for testing",
  "project_id": 1,
  "due_date": "2025-09-01T00:00:00Z",
  "sprint_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Beta Release",
  "description": "First beta version ready for testing",
  "project_id": 1,
  "sprint_id": 1,
  "due_date": "2025-09-01T00:00:00Z",
  "completed_at": null,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": null
}
```

### GET /milestones/
**Description:** Get all milestones

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `project_id` (optional): Filter by project

**Response:**
```json
[
  {
    "id": 1,
    "name": "Beta Release",
    "description": "First beta version ready for testing",
    "project_id": 1,
    "sprint_id": 1,
    "due_date": "2025-09-01T00:00:00Z",
    "completed_at": null,
    "created_at": "2025-07-21T10:30:00Z",
    "updated_at": null
  }
]
```

### PUT /milestones/{milestone_id}
**Description:** Update milestone

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Updated Beta Release",
  "description": "Updated description for beta release",
  "due_date": "2025-09-15T00:00:00Z",
  "sprint_id": 2
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Beta Release",
  "description": "Updated description for beta release",
  "project_id": 1,
  "sprint_id": 2,
  "due_date": "2025-09-15T00:00:00Z",
  "completed_at": null,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": "2025-07-21T11:30:00Z"
}
```

### PATCH /milestones/{milestone_id}/complete
**Description:** Mark milestone as completed

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "name": "Beta Release",
  "description": "First beta version ready for testing",
  "project_id": 1,
  "sprint_id": 1,
  "due_date": "2025-09-01T00:00:00Z",
  "completed_at": "2025-09-01T14:30:00Z",
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": "2025-09-01T14:30:00Z"
}
```

### PATCH /milestones/{milestone_id}/reopen
**Description:** Reopen completed milestone

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "name": "Beta Release",
  "description": "First beta version ready for testing",
  "project_id": 1,
  "sprint_id": 1,
  "due_date": "2025-09-01T00:00:00Z",
  "completed_at": null,
  "created_at": "2025-07-21T10:30:00Z",
  "updated_at": "2025-09-02T10:00:00Z"
}
```

---

## Time Logs Management

### POST /time-logs/
**Description:** Create a new time log

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "task_id": 1,
  "hours": 4.5,
  "description": "Implemented login form validation",
  "date": "2025-07-21"
}
```

**Response:**
```json
{
  "id": 1,
  "task_id": 1,
  "user_id": 2,
  "hours": 4.5,
  "description": "Implemented login form validation",
  "date": "2025-07-21",
  "created_at": "2025-07-21T15:30:00Z",
  "task": {
    "id": 1,
    "title": "Implement user authentication"
  },
  "user": {
    "id": 2,
    "username": "developer",
    "full_name": "Developer User"
  }
}
```

### GET /time-logs/
**Description:** Get time logs

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `task_id` (optional): Filter by task
- `user_id` (optional): Filter by user
- `date_from` (optional): Filter from date (YYYY-MM-DD)
- `date_to` (optional): Filter to date (YYYY-MM-DD)

**Response:**
```json
[
  {
    "id": 1,
    "task_id": 1,
    "user_id": 2,
    "hours": 4.5,
    "description": "Implemented login form validation",
    "date": "2025-07-21",
    "created_at": "2025-07-21T15:30:00Z",
    "task": {
      "id": 1,
      "title": "Implement user authentication"
    }
  }
]
```

---

## Backlogs Management

### POST /backlogs/
**Description:** Create a new backlog item

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "title": "User Profile Management",
  "description": "Allow users to manage their profiles",
  "priority": "medium",
  "story_points": 5,
  "project_id": 1
}
```

**Response:**
```json
{
  "id": 1,
  "title": "User Profile Management",
  "description": "Allow users to manage their profiles",
  "priority": "medium",
  "story_points": 5,
  "project_id": 1,
  "status": "open",
  "created_by_id": 1,
  "created_at": "2025-07-21T10:30:00Z",
  "project": {
    "id": 1,
    "name": "E-commerce Platform"
  }
}
```

### GET /backlogs/
**Description:** Get backlog items

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `project_id` (optional): Filter by project
- `status` (optional): Filter by status

**Response:**
```json
[
  {
    "id": 1,
    "title": "User Profile Management",
    "description": "Allow users to manage their profiles",
    "priority": "medium",
    "story_points": 5,
    "project_id": 1,
    "status": "open",
    "created_at": "2025-07-21T10:30:00Z"
  }
]
```

### POST /backlogs/{backlog_id}/convert-to-task
**Description:** Convert backlog item to task

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "assignee_id": 2,
  "sprint_id": 1,
  "estimated_hours": 20.0
}
```

**Response:**
```json
{
  "message": "Backlog item converted to task successfully",
  "task_id": 2
}
```

---

## Bug Reports Management

### POST /bug-reports/
**Description:** Create a new bug report

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "title": "Login button not responsive",
  "description": "The login button doesn't respond to clicks on mobile devices",
  "severity": "high",
  "priority": "high",
  "task_id": 1,
  "steps_to_reproduce": "1. Open mobile browser\n2. Navigate to login page\n3. Try clicking login button"
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Login button not responsive",
  "description": "The login button doesn't respond to clicks on mobile devices",
  "severity": "high",
  "priority": "high",
  "status": "open",
  "task_id": 1,
  "reporter_id": 1,
  "assignee_id": null,
  "steps_to_reproduce": "1. Open mobile browser\n2. Navigate to login page\n3. Try clicking login button",
  "created_at": "2025-07-21T10:30:00Z",
  "task": {
    "id": 1,
    "title": "Implement user authentication"
  },
  "reporter": {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User"
  }
}
```

### GET /bug-reports/
**Description:** Get bug reports

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `status` (optional): Filter by status
- `severity` (optional): Filter by severity
- `assignee_id` (optional): Filter by assignee

**Response:**
```json
[
  {
    "id": 1,
    "title": "Login button not responsive",
    "description": "The login button doesn't respond to clicks on mobile devices",
    "severity": "high",
    "priority": "high",
    "status": "open",
    "task_id": 1,
    "created_at": "2025-07-21T10:30:00Z"
  }
]
```

---

## Dashboard

### GET /dashboard/dashboard
**Description:** Get dashboard data for the current user

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "projects": {
    "total": 5,
    "active": 3
  },
  "tasks": {
    "total": 25,
    "my_tasks": 8,
    "todo": 3,
    "in_progress": 2,
    "completed": 3
  },
  "sprints": {
    "active": 2
  },
  "time_logs": {
    "total_hours": 45.5
  },
  "recent_tasks": [
    {
      "id": 1,
      "title": "Implement user authentication",
      "status": "in_progress",
      "priority": "high"
    }
  ]
}
```

### GET /dashboard/kanban/{project_id}
**Description:** Get kanban board data for a project

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "project": {
    "id": 1,
    "name": "E-commerce Platform"
  },
  "columns": {
    "todo": [
      {
        "id": 2,
        "title": "Setup database schema",
        "description": "Create initial database structure",
        "priority": "medium",
        "story_points": 3,
        "assignee": {
          "id": 2,
          "username": "developer",
          "full_name": "Developer User"
        },
        "due_date": "2025-07-25T17:00:00Z"
      }
    ],
    "in_progress": [
      {
        "id": 1,
        "title": "Implement user authentication",
        "description": "Create login and registration functionality",
        "priority": "high",
        "story_points": 8,
        "assignee": {
          "id": 2,
          "username": "developer",
          "full_name": "Developer User"
        },
        "due_date": "2025-07-28T17:00:00Z"
      }
    ],
    "review": [],
    "done": [],
    "blocked": []
  }
}
```

---

## Reports

### GET /reports/time-logs
**Description:** Get time logs report

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `user_id` (optional): Filter by user
- `project_id` (optional): Filter by project

**Response:**
```json
{
  "total_hours": 120.5,
  "total_entries": 25,
  "date_range": {
    "from": "2025-07-01",
    "to": "2025-07-21"
  },
  "by_user": [
    {
      "user_id": 2,
      "username": "developer",
      "full_name": "Developer User",
      "total_hours": 85.0,
      "entries_count": 18
    }
  ],
  "by_project": [
    {
      "project_id": 1,
      "project_name": "E-commerce Platform",
      "total_hours": 120.5,
      "entries_count": 25
    }
  ],
  "by_date": [
    {
      "date": "2025-07-21",
      "total_hours": 8.5,
      "entries_count": 3
    }
  ]
}
```

### GET /reports/story-points
**Description:** Get story points report

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `project_id` (optional): Filter by project
- `sprint_id` (optional): Filter by sprint

**Response:**
```json
{
  "total_story_points": 45,
  "completed_story_points": 28,
  "completion_rate": 62.22,
  "by_status": {
    "todo": 8,
    "in_progress": 9,
    "review": 0,
    "done": 28,
    "blocked": 0
  },
  "by_project": [
    {
      "project_id": 1,
      "project_name": "E-commerce Platform",
      "total_story_points": 45,
      "completed_story_points": 28,
      "completion_rate": 62.22
    }
  ]
}
```

### GET /reports/teams
**Description:** Get teams report

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "total_teams": 3,
  "active_teams": 3,
  "teams": [
    {
      "team_id": 1,
      "team_name": "Development Team Alpha",
      "leader": {
        "id": 2,
        "username": "teamlead",
        "full_name": "Team Leader"
      },
      "member_count": 4,
      "project_count": 2,
      "task_statistics": {
        "total_tasks": 15,
        "completed_tasks": 8,
        "in_progress_tasks": 4,
        "completion_rate": 53.33
      },
      "total_hours_logged": 145.5
    }
  ]
}
```

### GET /reports/dashboard
**Description:** Get comprehensive dashboard report

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "overview": {
    "total_projects": 5,
    "active_projects": 3,
    "total_teams": 3,
    "total_users": 12,
    "total_tasks": 45,
    "completed_tasks": 28
  },
  "project_health": [
    {
      "project_id": 1,
      "project_name": "E-commerce Platform",
      "status": "active",
      "completion_rate": 62.22,
      "tasks_overdue": 2,
      "team_count": 1
    }
  ],
  "team_productivity": [
    {
      "team_id": 1,
      "team_name": "Development Team Alpha",
      "tasks_completed_this_week": 3,
      "hours_logged_this_week": 32.5,
      "velocity": 15
    }
  ],
  "recent_activities": [
    {
      "type": "task_completed",
      "description": "Task 'Implement user authentication' completed",
      "timestamp": "2025-07-21T14:30:00Z",
      "user": "Developer User"
    }
  ]
}
```

---

## Analytics (Advanced Reports)

### GET /analytics/productivity-summary
**Description:** Get productivity summary analytics

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `team_id` (optional): Filter by team

**Response:**
```json
{
  "summary": {
    "total_tasks_completed": 28,
    "total_hours_logged": 245.5,
    "average_task_completion_time": 8.77,
    "productivity_score": 82.5
  },
  "team_performance": [
    {
      "team_id": 1,
      "team_name": "Development Team Alpha",
      "tasks_completed": 15,
      "hours_logged": 145.5,
      "velocity": 18,
      "efficiency_score": 85.2
    }
  ],
  "user_performance": [
    {
      "user_id": 2,
      "username": "developer",
      "full_name": "Developer User",
      "tasks_completed": 8,
      "hours_logged": 65.5,
      "average_hours_per_task": 8.19,
      "productivity_score": 78.5
    }
  ]
}
```

### GET /analytics/burndown-chart
**Description:** Get burndown chart data

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `sprint_id` (required): Sprint ID
- `project_id` (optional): Project ID

**Response:**
```json
{
  "sprint": {
    "id": 1,
    "name": "Sprint 1 - Authentication",
    "start_date": "2025-07-21",
    "end_date": "2025-08-04",
    "total_story_points": 45
  },
  "burndown_data": [
    {
      "date": "2025-07-21",
      "remaining_story_points": 45,
      "ideal_remaining": 45,
      "tasks_completed": 0
    },
    {
      "date": "2025-07-22",
      "remaining_story_points": 37,
      "ideal_remaining": 42,
      "tasks_completed": 2
    }
  ],
  "velocity": 3.2,
  "projected_completion": "2025-08-03"
}
```

### GET /analytics/workload-analysis
**Description:** Get workload analysis

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `team_id` (optional): Filter by team

**Response:**
```json
{
  "team_workload": [
    {
      "team_id": 1,
      "team_name": "Development Team Alpha",
      "total_capacity": 160,
      "allocated_hours": 145.5,
      "utilization_rate": 90.94,
      "overload_risk": "medium"
    }
  ],
  "user_workload": [
    {
      "user_id": 2,
      "username": "developer",
      "full_name": "Developer User",
      "capacity": 40,
      "allocated_hours": 38.5,
      "utilization_rate": 96.25,
      "current_tasks": 3,
      "overload_risk": "high"
    }
  ],
  "recommendations": [
    "Consider redistributing tasks from Developer User who has 96% utilization",
    "Team Alpha is operating at optimal capacity"
  ]
}
```

### GET /analytics/export/csv
**Description:** Export analytics data to CSV

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `report_type` (required): Type of report (time_logs, tasks, story_points)
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Response:** CSV file download

### GET /analytics/export/json
**Description:** Export analytics data to JSON

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `report_type` (required): Type of report
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Response:**
```json
{
  "export_type": "time_logs",
  "generated_at": "2025-07-21T16:30:00Z",
  "date_range": {
    "from": "2025-07-01",
    "to": "2025-07-21"
  },
  "data": [
    {
      "id": 1,
      "user": "Developer User",
      "task": "Implement user authentication",
      "project": "E-commerce Platform",
      "hours": 4.5,
      "date": "2025-07-21",
      "description": "Implemented login form validation"
    }
  ],
  "summary": {
    "total_records": 25,
    "total_hours": 120.5
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Enums and Constants

### User Roles
- `admin` - Full system access
- `project_manager` - Can manage projects and teams
- `team_leader` - Can manage team tasks and sprints
- `developer` - Can work on assigned tasks
- `tester` - Can test and report bugs
- `viewer` - Read-only access

### Task Status
- `todo` - Not started
- `in_progress` - Currently being worked on
- `review` - Under review
- `done` - Completed
- `blocked` - Blocked by dependencies

### Task Priority
- `low` - Low priority
- `medium` - Medium priority
- `high` - High priority
- `urgent` - Urgent priority

### Project Status
- `active` - Currently active
- `on_hold` - Temporarily paused
- `completed` - Finished
- `cancelled` - Cancelled

### Sprint Status
- `planned` - Not yet started
- `active` - Currently running
- `completed` - Finished
- `cancelled` - Cancelled

---

## Rate Limiting and Pagination

### Pagination
Most list endpoints support pagination with `skip` and `limit` parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)

### Filters
Many endpoints support filtering. Common filter parameters:
- `project_id`: Filter by project
- `user_id`: Filter by user
- `status`: Filter by status
- `date_from`/`date_to`: Date range filters

---

## WebSocket Support (Future Enhancement)

The API is designed to support real-time updates via WebSocket connections for:
- Task status changes
- New comments and updates
- Sprint progress
- Team notifications

---

## Testing the API

You can test the API using:

1. **Swagger UI**: `http://localhost:8000/docs`
2. **ReDoc**: `http://localhost:8000/redoc`
3. **cURL**: As shown in examples above
4. **Postman**: Import the OpenAPI specification from `/openapi.json`

### Authentication Flow for Testing

1. Login to get access token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
```

2. Use the token in subsequent requests:
```bash
curl -X GET "http://localhost:8000/api/v1/projects/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
