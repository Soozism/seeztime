# Ginga Tek Task Management API - Copilot Instructions

This is a FastAPI-based task management system with role-based access control, team-based project management, and comprehensive CRUD operations.

## Architecture Patterns

### Project Structure
- `app/models/` - SQLAlchemy ORM models with relationships and constraints
- `app/schemas/` - Pydantic models for request/response validation (suffix with Create/Update/Response)
- `app/api/v1/endpoints/` - FastAPI route handlers with consistent permission patterns
- `app/core/` - Shared utilities (auth, database, config)
- `scripts/` - Database initialization and utility scripts

### Key Models & Relationships
- **User** → **Team** (many-to-many via team membership)
- **Team** → **Project** (many-to-many via assignments)
- **Project** → **Task/Sprint/Milestone** (one-to-many)
- **Task** → **Task** (self-referential for subtasks via `parent_task_id`)

### Permission System Patterns
All endpoints use role-based functions that check team-project relationships:

```python
def can_manage_sprints_in_project(user: User, project: Project, db: Session) -> bool:
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    if user.role == UserRole.TEAM_LEADER:
        return db.query(Team).filter(
            Team.team_leader_id == user.id,
            Team.projects.any(Project.id == project.id)
        ).first() is not None
    return False
```

**Role Hierarchy**: Admin > Project Manager > Team Leader > Developer/Tester > Viewer

## Development Patterns

### Endpoint Structure
Each endpoint file follows this pattern:
1. Permission helper functions at top
2. GET endpoints (with role-based filtering)
3. POST/PUT/DELETE endpoints (with permission checks)
4. Status update PATCH endpoints

### Schema Naming Convention
- `{Entity}Base` - Common fields
- `{Entity}Create` - Required fields for creation
- `{Entity}Update` - Optional fields for updates (all Optional)
- `{Entity}Response` - Output model with computed fields

### Authentication Flow
- JWT tokens with username in `sub` claim
- `get_current_active_user` dependency for protected endpoints
- Permission checks happen after authentication, not in auth layer

## Critical Commands

### Development Setup
```bash
python scripts/create_admin.py  # Creates admin user (admin/admin123)
python main.py                  # Starts server on localhost:8000
python -m pytest test_main.py  # Runs core API tests
```

### Database Operations
- Uses SQLite by default (`ginga_tek.db`)
- Alembic migrations in `migrations/versions/`
- Test database (`test.db`) auto-cleaned between tests

## Special Considerations

### Team-Project Authorization
Unlike simple role checks, this system uses team membership for project access. Team leaders can manage resources (tasks, sprints, milestones) only in their assigned projects.

### Enum Usage
- `TaskPriority` is IntEnum (1=LOW, 2=MEDIUM, 3=HIGH, 4=CRITICAL)
- All other enums are string-based
- Always use enum values in API calls, not strings

### Time Tracking
- `TimeLog` entries automatically update `Task.actual_hours`
- Handle time calculations in update operations

### Expanded Responses
Many endpoints support `?expand=true` for related data:
```python
# Returns task with project_name, assignee_name, etc.
TaskResponse.from_orm_with_expansions(task)
```

### Test Database Isolation
Tests use `@pytest.fixture(autouse=True)` to drop/recreate tables between tests. Production DB is separate.

## Common Patterns to Follow

- Always check permissions before DB operations
- Use `exclude_unset=True` for partial updates
- Add proper foreign key constraints with `nullable=False` for required relationships
- Include `created_at`/`updated_at` timestamps on all entities
- Use consistent error messages (404 for "not found", 403 for "permission denied")
