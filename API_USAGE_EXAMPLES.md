"""
Comprehensive API Usage Examples for Advanced Queries

This file demonstrates how to use all the new advanced query endpoints
with various filtering options and real-world scenarios.
"""

# Example 1: Get tasks for a specific sprint with time filtering
# Useful for sprint reviews and progress tracking

GET /api/v1/queries/tasks/by-sprint/123
GET /api/v1/queries/tasks/by-sprint/123?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z

# Example 2: Get all tasks assigned to a user in the last 30 days
# Useful for performance reviews and workload analysis

GET /api/v1/queries/tasks/by-user/456?start_date=2025-06-22T00:00:00Z&end_date=2025-07-22T23:59:59Z

# Example 3: Get all sprints for a project created in Q2 2025
# Useful for project planning and retrospectives

GET /api/v1/queries/sprints/by-project/789?start_date=2025-04-01T00:00:00Z&end_date=2025-06-30T23:59:59Z

# Example 4: Get all sprints where a user has tasks (user involvement)
# Useful for resource allocation and team coordination

GET /api/v1/queries/sprints/by-user/456

# Example 5: Get all projects where a user is involved (team or tasks)
# Useful for user dashboards and access management

GET /api/v1/queries/projects/by-user/456

# Example 6: Get time logs for a user in a specific week
# Useful for timesheet verification and billing

GET /api/v1/queries/time-logs/by-user/456?start_date=2025-07-21T00:00:00Z&end_date=2025-07-27T23:59:59Z

# Example 7: Get all time logs for a specific task
# Useful for task analysis and effort tracking

GET /api/v1/queries/time-logs/by-task/123

# Example 8: Get time logs for all tasks in a sprint
# Useful for sprint burndown and velocity calculations

GET /api/v1/queries/time-logs/by-sprint/789?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z

# Example 9: Get time logs for all tasks in a project
# Useful for project billing and cost analysis

GET /api/v1/queries/time-logs/by-project/456

# Example 10: Get milestones for a sprint
# Useful for milestone tracking and deliverable management

GET /api/v1/queries/milestones/by-sprint/123

# Example 11: Get all milestones for a project
# Useful for project roadmap and progress tracking

GET /api/v1/queries/milestones/by-project/456

# Example 12: Get user time summary for billing period
# Useful for payroll and client billing

GET /api/v1/queries/summary/user/456/time-logs?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z

# Response:
{
  "user_id": 456,
  "total_hours": 120.5,
  "start_date": "2025-07-01T00:00:00Z",
  "end_date": "2025-07-31T23:59:59Z"
}

# Example 13: Get project time summary for cost analysis
# Useful for project budgeting and resource allocation

GET /api/v1/queries/summary/project/789/time-logs?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z

# Response:
{
  "project_id": 789,
  "total_hours": 450.25,
  "start_date": "2025-07-01T00:00:00Z",
  "end_date": "2025-07-31T23:59:59Z"
}

# Example 14: Get sprint time summary for velocity calculation
# Useful for sprint planning and team performance metrics

GET /api/v1/queries/summary/sprint/123/time-logs

# Response:
{
  "sprint_id": 123,
  "total_hours": 85.75,
  "start_date": null,
  "end_date": null
}

# Example 15: Enhanced time logs endpoint with filters
# The existing time logs endpoint now supports time filtering

GET /api/v1/time-logs/?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z&user_id=456

# Example 16: Pagination with large datasets
# All endpoints support pagination for better performance

GET /api/v1/queries/tasks/by-user/456?skip=0&limit=50
GET /api/v1/queries/tasks/by-user/456?skip=50&limit=50

# Example 17: Complex filtering scenarios

# Get tasks assigned to user in specific sprint during July 2025
GET /api/v1/queries/tasks/by-sprint/123?start_date=2025-07-01T00:00:00Z&end_date=2025-07-31T23:59:59Z
# Then filter by assignee_id in your application logic

# Get time logs for project tasks in specific date range
GET /api/v1/queries/time-logs/by-project/456?start_date=2025-07-15T00:00:00Z&end_date=2025-07-22T23:59:59Z

# Real-world use case examples:

# Use Case 1: Sprint Review Dashboard
# Combine multiple endpoints to show sprint progress
"""
1. GET /api/v1/queries/tasks/by-sprint/{sprint_id} - All tasks in sprint
2. GET /api/v1/queries/time-logs/by-sprint/{sprint_id} - All time logged
3. GET /api/v1/queries/summary/sprint/{sprint_id}/time-logs - Total hours
4. GET /api/v1/queries/milestones/by-sprint/{sprint_id} - Sprint milestones
"""

# Use Case 2: User Performance Report
# Track user productivity across projects
"""
1. GET /api/v1/queries/tasks/by-user/{user_id}?start_date=X&end_date=Y - Tasks assigned
2. GET /api/v1/queries/time-logs/by-user/{user_id}?start_date=X&end_date=Y - Time logged
3. GET /api/v1/queries/summary/user/{user_id}/time-logs?start_date=X&end_date=Y - Total hours
4. GET /api/v1/queries/projects/by-user/{user_id} - Projects involved in
"""

# Use Case 3: Project Cost Analysis
# Calculate project costs and resource utilization
"""
1. GET /api/v1/queries/time-logs/by-project/{project_id}?start_date=X&end_date=Y - All time logs
2. GET /api/v1/queries/summary/project/{project_id}/time-logs?start_date=X&end_date=Y - Total hours
3. GET /api/v1/queries/sprints/by-project/{project_id} - All sprints
4. Group time logs by user and calculate costs based on hourly rates
"""

# Use Case 4: Team Workload Balancing
# Distribute work evenly across team members
"""
1. For each team member:
   - GET /api/v1/queries/tasks/by-user/{user_id} - Current tasks
   - GET /api/v1/queries/summary/user/{user_id}/time-logs?start_date=X&end_date=Y - Recent hours
2. Compare workloads and reassign tasks as needed
"""

# Use Case 5: Client Billing
# Generate accurate billing reports for clients
"""
1. GET /api/v1/queries/time-logs/by-project/{project_id}?start_date=X&end_date=Y - Billable hours
2. Group by user and task type
3. Apply billing rates
4. Generate invoice
"""

# Authentication Example:
"""
# 1. Login first
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password123"
}

# 2. Use the returned token in Authorization header
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# 3. Make API calls with the token
GET /api/v1/queries/tasks/by-user/123
Headers: {
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
"""

# Error Handling Examples:
"""
# 404 - Resource not found
GET /api/v1/queries/tasks/by-sprint/99999
Response: {"detail": "Sprint not found"}

# 403 - Insufficient permissions
GET /api/v1/queries/tasks/by-user/999 (trying to access another user's tasks)
Response: {"detail": "Access denied to other user's tasks"}

# 400 - Invalid date format
GET /api/v1/queries/tasks/by-user/123?start_date=invalid-date
Response: {"detail": "Invalid date format"}
"""

# Performance Tips:
"""
1. Use pagination (skip/limit) for large datasets
2. Use specific date ranges to reduce query size
3. Cache frequently accessed data on the client side
4. Use summary endpoints for aggregated data instead of fetching all records
5. Combine multiple API calls efficiently in your frontend
"""
