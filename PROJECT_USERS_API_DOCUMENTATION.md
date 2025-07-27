# Project User Statistics API Enhancement

This document describes the new user statistics features added to the project management API.

## New Features

### 1. Enhanced Project Detail Endpoint

**Endpoint**: `GET /projects/{project_id}`

**New Query Parameters**:
- `include_users` (boolean, default: true): Include user statistics in the response

**New Response Fields**:
```json
{
  "users_summary": {
    "total_project_hours": 45.5,
    "total_project_story_points": 34,
    "active_users_count": 3,
    "users_stats": [
      {
        "user_id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "total_hours": 23.5,
        "total_story_points": 21,
        "tasks_completed": 5,
        "tasks_in_progress": 2,
        "tasks_total": 7
      }
    ]
  }
}
```

### 2. Dedicated Project Users Endpoint

**Endpoint**: `GET /projects/{project_id}/users`

**Description**: Get detailed statistics for all users working on a specific project.

**Response Format**:
```json
{
  "project_id": 1,
  "project_name": "My Project",
  "total_project_hours": 120.5,
  "total_project_story_points": 89,
  "active_users_count": 4,
  "users_stats": [
    {
      "user_id": 1,
      "username": "developer1",
      "first_name": "Alice",
      "last_name": "Johnson",
      "full_name": "Alice Johnson",
      "email": "alice@company.com",
      "role": "DEVELOPER",
      "total_hours": 35.5,
      "total_story_points": 28,
      "tasks_completed": 6,
      "tasks_in_progress": 1,
      "tasks_todo": 2,
      "tasks_review": 1,
      "tasks_total": 10
    }
  ]
}
```

## Data Calculations

### Time Tracking
- **total_hours**: Sum of all time log entries for tasks assigned to the user in this project
- **total_project_hours**: Sum of all time log entries for all users in the project

### Story Points
- **total_story_points**: Sum of story points from all tasks assigned to the user in this project
- **total_project_story_points**: Sum of story points from all tasks in the project

### Task Statistics
- **tasks_completed**: Count of tasks with status "DONE"
- **tasks_in_progress**: Count of tasks with status "IN_PROGRESS"  
- **tasks_todo**: Count of tasks with status "TODO"
- **tasks_review**: Count of tasks with status "REVIEW"
- **tasks_total**: Total count of all tasks assigned to the user

## Usage Examples

### Get Project with User Statistics
```bash
curl -X GET "/projects/1?include_users=true&expand=true&include_details=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Only User Statistics for a Project
```bash
curl -X GET "/projects/1/users" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Project without User Statistics (for performance)
```bash
curl -X GET "/projects/1?include_users=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Performance Considerations

- User statistics calculations involve complex JOINs across multiple tables
- Use `include_users=false` when you don't need user statistics to improve performance
- The dedicated `/projects/{id}/users` endpoint is optimized for user statistics only
- Statistics are calculated in real-time, so expect slight delays for projects with many tasks and time logs

## Database Schema Dependencies

This feature relies on the following relationships:
- `Task.assignee_id` → `User.id`
- `Task.project_id` → `Project.id`
- `TimeLog.user_id` → `User.id`
- `TimeLog.task_id` → `Task.id`
- `Task.story_points` field
- `TimeLog.hours` field

## Error Handling

- Returns 404 if project not found
- Returns empty arrays if no users are assigned to project tasks
- Handles null values gracefully (users with no time logs, tasks with no story points, etc.)
