# Advanced Query APIs Documentation

This document describes the comprehensive set of APIs for querying tasks, sprints, projects, time logs, and milestones with time filtering capabilities.

## Base URL
All endpoints are prefixed with `/api/v1/queries`

## Authentication
All endpoints require authentication. Include the JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Common Parameters

### Time Filtering
Most endpoints support time filtering with these optional query parameters:
- `start_date`: Filter results from this date onwards (ISO 8601 format)
- `end_date`: Filter results up to this date (ISO 8601 format)

### Pagination
Most list endpoints support pagination:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

## Task Query Endpoints

### Get Tasks by Sprint
**GET** `/tasks/by-sprint/{sprint_id}`

Get all tasks for a specific sprint with time filtering.

**Parameters:**
- `sprint_id` (path): Sprint ID
- `start_date` (query, optional): Filter by task creation date
- `end_date` (query, optional): Filter by task creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of TaskResponse objects

**Example:**
```bash
GET /api/v1/queries/tasks/by-sprint/123?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z
```

### Get Tasks by User
**GET** `/tasks/by-user/{user_id}`

Get all tasks assigned to a specific user with time filtering.

**Parameters:**
- `user_id` (path): User ID
- `start_date` (query, optional): Filter by task creation date
- `end_date` (query, optional): Filter by task creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of TaskResponse objects

**Access Control:** Users can only access their own tasks unless they are Admin/PM.

## Sprint Query Endpoints

### Get Sprints by Project
**GET** `/sprints/by-project/{project_id}`

Get all sprints for a specific project with time filtering.

**Parameters:**
- `project_id` (path): Project ID
- `start_date` (query, optional): Filter by sprint creation date
- `end_date` (query, optional): Filter by sprint creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of SprintResponse objects

### Get Sprints by User
**GET** `/sprints/by-user/{user_id}`

Get all sprints where the user has assigned tasks.

**Parameters:**
- `user_id` (path): User ID
- `start_date` (query, optional): Filter by sprint creation date
- `end_date` (query, optional): Filter by sprint creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of SprintResponse objects

## Project Query Endpoints

### Get Projects by User
**GET** `/projects/by-user/{user_id}`

Get all projects where the user is involved (through team membership or task assignment).

**Parameters:**
- `user_id` (path): User ID
- `start_date` (query, optional): Filter by project creation date
- `end_date` (query, optional): Filter by project creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of ProjectResponse objects

## Time Log Query Endpoints

### Get Time Logs by User
**GET** `/time-logs/by-user/{user_id}`

Get all time logs for a specific user with time filtering.

**Parameters:**
- `user_id` (path): User ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of TimeLogResponse objects

**Note:** For time logs, the date filtering is applied to the `date` field (when the work was done), not the creation date.

### Get Time Logs by Task
**GET** `/time-logs/by-task/{task_id}`

Get all time logs for a specific task with time filtering.

**Parameters:**
- `task_id` (path): Task ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of TimeLogResponse objects

### Get Time Logs by Sprint
**GET** `/time-logs/by-sprint/{sprint_id}`

Get all time logs for tasks in a specific sprint.

**Parameters:**
- `sprint_id` (path): Sprint ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of TimeLogResponse objects

### Get Time Logs by Project
**GET** `/time-logs/by-project/{project_id}`

Get all time logs for tasks in a specific project.

**Parameters:**
- `project_id` (path): Project ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of TimeLogResponse objects

## Milestone Query Endpoints

### Get Milestones by Sprint
**GET** `/milestones/by-sprint/{sprint_id}`

Get all milestones for a specific sprint.

**Parameters:**
- `sprint_id` (path): Sprint ID
- `start_date` (query, optional): Filter by milestone creation date
- `end_date` (query, optional): Filter by milestone creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of MilestoneResponse objects

### Get Milestones by Project
**GET** `/milestones/by-project/{project_id}`

Get all milestones for a specific project (through its sprints).

**Parameters:**
- `project_id` (path): Project ID
- `start_date` (query, optional): Filter by milestone creation date
- `end_date` (query, optional): Filter by milestone creation date
- `skip` (query, optional): Pagination offset
- `limit` (query, optional): Pagination limit

**Response:** Array of MilestoneResponse objects

## Summary/Aggregation Endpoints

### Get User Time Summary
**GET** `/summary/user/{user_id}/time-logs`

Get aggregated time log summary for a user.

**Parameters:**
- `user_id` (path): User ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date

**Response:**
```json
{
  "user_id": 123,
  "total_hours": 45.5,
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z"
}
```

### Get Project Time Summary
**GET** `/summary/project/{project_id}/time-logs`

Get aggregated time log summary for a project.

**Parameters:**
- `project_id` (path): Project ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date

**Response:**
```json
{
  "project_id": 456,
  "total_hours": 120.25,
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z"
}
```

### Get Sprint Time Summary
**GET** `/summary/sprint/{sprint_id}/time-logs`

Get aggregated time log summary for a sprint.

**Parameters:**
- `sprint_id` (path): Sprint ID
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date

**Response:**
```json
{
  "sprint_id": 789,
  "total_hours": 67.75,
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-01-31T23:59:59Z"
}
```

## Access Control

The APIs implement role-based access control:

- **Admin/Project Manager**: Can access all data
- **Team Leader**: Can access data for projects their teams are assigned to
- **Team Member**: Can access data for projects their teams are assigned to
- **Individual Users**: Can only access their own data (tasks, time logs, etc.)

## Error Responses

Common error responses:

- **404 Not Found**: Resource doesn't exist
- **403 Forbidden**: Insufficient permissions
- **400 Bad Request**: Invalid parameters
- **401 Unauthorized**: Authentication required

## Example Usage

### Get tasks for a sprint in January 2025
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/queries/tasks/by-sprint/123?start_date=2025-01-01T00:00:00Z&end_date=2025-01-31T23:59:59Z"
```

### Get time logs for a user with pagination
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/queries/time-logs/by-user/456?skip=0&limit=50"
```

### Get project time summary for current month
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/queries/summary/project/789/time-logs?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z"
```

## Enhanced Time Logs Endpoint

The existing time logs endpoint (`/api/v1/time-logs/`) has also been enhanced with time filtering:

**GET** `/api/v1/time-logs/`

**Additional Parameters:**
- `start_date` (query, optional): Filter by log date
- `end_date` (query, optional): Filter by log date

This provides backward compatibility while adding the requested time filtering functionality.

## Date Format

All date parameters should be in ISO 8601 format:
- `2025-07-22T00:00:00Z` (with timezone)
- `2025-07-22T00:00:00` (without timezone, treated as UTC)
- `2025-07-22` (date only, treated as start of day UTC)
