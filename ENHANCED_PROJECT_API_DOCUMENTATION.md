# Enhanced Project API Documentation

## Overview
The project endpoint has been enhanced to provide comprehensive statistics and detailed information about tasks, sprints, and milestones associated with the project.

## Endpoint
**GET** `/api/v1/projects/{project_id}`

## Parameters

### Path Parameters
- `project_id` (integer, required): The ID of the project to retrieve

### Query Parameters
- `expand` (boolean, optional, default: true): Include expanded user information
- `include_details` (boolean, optional, default: false): Include detailed lists of tasks, sprints, and milestones

## Response Structure

### Base Project Information
```json
{
  "id": 1,
  "name": "My Project",
  "description": "Project description",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "status": "ACTIVE",
  "created_by_id": 1,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-07-22T10:30:00Z"
}
```

### Expanded User Information (when expand=true)
```json
{
  "created_by_username": "admin@example.com",
  "created_by_name": "John Doe"
}
```

### Task Summary Statistics
```json
{
  "task_summary": {
    "total": 25,
    "todo": 8,
    "in_progress": 10,
    "review": 4,
    "done": 3,
    "todo_percentage": 32.0,
    "in_progress_percentage": 40.0,
    "review_percentage": 16.0,
    "done_percentage": 12.0
  }
}
```

### Sprint Summary Statistics
```json
{
  "sprint_summary": {
    "total": 5,
    "planned": 2,
    "active": 1,
    "completed": 2,
    "planned_percentage": 40.0,
    "active_percentage": 20.0,
    "completed_percentage": 40.0
  }
}
```

### Milestone Summary Statistics
```json
{
  "milestone_summary": {
    "total": 8,
    "pending": 5,
    "completed": 3,
    "pending_percentage": 62.5,
    "completed_percentage": 37.5
  }
}
```

### Detailed Task Information (when include_details=true)
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Implement user authentication",
      "description": "Add JWT-based authentication system",
      "status": "IN_PROGRESS",
      "priority": "HIGH",
      "story_points": 8,
      "estimated_hours": 16.0,
      "actual_hours": 12.5,
      "created_at": "2025-01-15T09:00:00Z",
      "updated_at": "2025-07-20T14:30:00Z",
      "due_date": "2025-07-25T23:59:59Z",
      "assignee_name": "Jane Smith",
      "assignee_username": "jane.smith@example.com",
      "sprint_name": "Sprint 1",
      "is_subtask": false
    }
  ]
}
```

### Detailed Sprint Information (when include_details=true)
```json
{
  "sprints": [
    {
      "id": 1,
      "name": "Sprint 1",
      "description": "Initial development sprint",
      "status": "ACTIVE",
      "start_date": "2025-07-01T00:00:00Z",
      "end_date": "2025-07-14T23:59:59Z",
      "created_at": "2025-06-25T00:00:00Z",
      "updated_at": "2025-07-01T00:00:00Z",
      "task_count": 12
    }
  ]
}
```

### Detailed Milestone Information (when include_details=true)
```json
{
  "milestones": [
    {
      "id": 1,
      "name": "MVP Release",
      "description": "Minimum viable product release",
      "due_date": "2025-08-01T00:00:00Z",
      "completed_at": null,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-07-22T00:00:00Z",
      "sprint_name": "Sprint 2",
      "is_completed": false
    }
  ]
}
```

## Complete Response Example

### Basic Response (expand=true, include_details=false)
```json
{
  "id": 1,
  "name": "E-commerce Platform",
  "description": "Complete e-commerce solution with admin panel",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-12-31T23:59:59Z",
  "status": "ACTIVE",
  "created_by_id": 1,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-07-22T10:30:00Z",
  "created_by_username": "admin@example.com",
  "created_by_name": "John Doe",
  "task_summary": {
    "total": 45,
    "todo": 15,
    "in_progress": 18,
    "review": 8,
    "done": 4,
    "todo_percentage": 33.33,
    "in_progress_percentage": 40.0,
    "review_percentage": 17.78,
    "done_percentage": 8.89
  },
  "sprint_summary": {
    "total": 6,
    "planned": 2,
    "active": 2,
    "completed": 2,
    "planned_percentage": 33.33,
    "active_percentage": 33.33,
    "completed_percentage": 33.33
  },
  "milestone_summary": {
    "total": 12,
    "pending": 8,
    "completed": 4,
    "pending_percentage": 66.67,
    "completed_percentage": 33.33
  }
}
```

## Usage Examples

### Get Project Summary Only
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/projects/1"
```

### Get Project with Detailed Lists
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/projects/1?include_details=true"
```

### Get Project without Expanded User Info
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/projects/1?expand=false"
```

## Key Features

### 📊 Comprehensive Statistics
- **Task Statistics**: Total tasks and breakdown by status (TODO, IN_PROGRESS, REVIEW, DONE)
- **Sprint Statistics**: Total sprints and breakdown by status (PLANNED, ACTIVE, COMPLETED)
- **Milestone Statistics**: Total milestones and breakdown by completion status

### 📈 Percentage Calculations
- All statistics include percentage breakdowns for easy visualization
- Percentages are calculated as (count / total) * 100 and rounded to 2 decimal places
- Zero division is handled gracefully (returns 0.0%)

### 📋 Detailed Information (Optional)
When `include_details=true`:
- **Complete Task List**: All tasks with assignee info, sprint association, and detailed metadata
- **Complete Sprint List**: All sprints with task counts and status information
- **Complete Milestone List**: All milestones with completion status and sprint association

### 🔒 Security & Access Control
- Requires authentication (JWT token)
- Respects existing project access permissions
- Role-based access control maintained

### ⚡ Performance Optimized
- Efficient database queries using aggregations
- Optional detailed loading (include_details parameter)
- Minimal N+1 query issues with proper joins

## Use Cases

### 1. Project Dashboard
Display comprehensive project overview with progress indicators:
- Task completion percentages for progress bars
- Sprint status for timeline visualization
- Milestone tracking for deliverable planning

### 2. Project Reporting
Generate detailed project reports:
- Task distribution analysis
- Sprint velocity calculations
- Milestone achievement tracking

### 3. Resource Planning
Understand project complexity and resource requirements:
- Task count and complexity (story points)
- Sprint planning and capacity
- Milestone dependencies

### 4. Project Health Monitoring
Track project health indicators:
- Task completion rates
- Sprint progress
- Milestone on-time delivery

### 5. Client Presentations
Present project status to stakeholders:
- High-level statistics for executive summaries
- Detailed progress for technical reviews
- Timeline and milestone tracking for planning

## Error Responses

### 404 Not Found
```json
{
  "detail": "Project not found"
}
```

### 403 Forbidden
```json
{
  "detail": "Access denied to this project"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

## Performance Notes

1. **Basic Request**: Fast response with aggregated statistics only
2. **Detailed Request**: Slightly slower due to additional joins and data loading
3. **Caching Recommended**: Consider caching responses for frequently accessed projects
4. **Pagination**: Detailed lists are not paginated - consider limiting for very large projects
