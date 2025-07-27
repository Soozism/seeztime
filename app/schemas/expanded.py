"""
Schema initialization to handle expanded responses without circular imports
"""

def setup_expanded_schemas():
    """Setup expanded schemas after all basic schemas are loaded"""
    
    # Import all the basic schemas first
    from app.schemas.user import UserSimple
    from app.schemas.project import ProjectSimple
    from app.schemas.sprint import SprintSimple
    
    # Now we can create the expanded schemas without forward references
    from pydantic import BaseModel
    from typing import Optional
    from datetime import datetime
    from app.models.enums import TaskStatus, TaskPriority, ProjectStatus, SprintStatus
    
    # Define expanded schemas here
    class TaskResponseExpanded(BaseModel):
        # Basic task fields
        id: int
        title: str
        description: Optional[str] = None
        status: TaskStatus = TaskStatus.TODO
        priority: TaskPriority = TaskPriority.MEDIUM
        story_points: int = 0
        estimated_hours: float = 0.0
        due_date: Optional[datetime] = None
        is_subtask: bool = False
        
        # IDs
        project_id: int
        sprint_id: Optional[int] = None
        assignee_id: Optional[int] = None
        created_by_id: int
        parent_task_id: Optional[int] = None
        
        # Expanded objects
        project: Optional[ProjectSimple] = None
        sprint: Optional[SprintSimple] = None
        assignee: Optional[UserSimple] = None
        created_by: Optional[UserSimple] = None
        
        # Additional fields
        actual_hours: float = 0.0
        created_at: datetime
        updated_at: Optional[datetime] = None

        class Config:
            from_attributes = True
    
    class ProjectResponseExpanded(BaseModel):
        # Basic project fields
        id: int
        name: str
        description: Optional[str] = None
        start_date: Optional[datetime] = None
        end_date: Optional[datetime] = None
        status: ProjectStatus = ProjectStatus.ACTIVE
        
        # IDs and expanded objects
        created_by_id: int
        created_by: Optional[UserSimple] = None
        
        # Additional fields
        created_at: datetime
        updated_at: Optional[datetime] = None

        class Config:
            from_attributes = True
    
    class SprintResponseExpanded(BaseModel):
        # Basic sprint fields
        id: int
        name: str
        description: Optional[str] = None
        status: SprintStatus = SprintStatus.PLANNED
        start_date: Optional[datetime] = None
        end_date: Optional[datetime] = None
        
        # IDs and expanded objects
        project_id: int
        project: Optional[ProjectSimple] = None
        
        # Additional fields
        created_at: datetime
        updated_at: Optional[datetime] = None

        class Config:
            from_attributes = True
    
    return TaskResponseExpanded, ProjectResponseExpanded, SprintResponseExpanded

# Store the schemas globally after they're created
_expanded_schemas = None

def get_expanded_schemas():
    """Get the expanded schemas, creating them if needed"""
    global _expanded_schemas
    if _expanded_schemas is None:
        _expanded_schemas = setup_expanded_schemas()
    return _expanded_schemas
