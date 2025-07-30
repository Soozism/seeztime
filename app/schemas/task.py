"""
Task schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.enums import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    story_points: int = 0
    estimated_hours: float = 0.0
    due_date: Optional[datetime] = None
    is_subtask: bool = False

class TaskCreate(TaskBase):
    project_id: int
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None
    parent_task_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    story_points: Optional[int] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    assignee_id: Optional[int] = None
    sprint_id: Optional[int] = None
    due_date: Optional[datetime] = None
    is_subtask: Optional[bool] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(TaskBase):
    id: int
    project_id: int
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None
    created_by_id: int
    parent_task_id: Optional[int] = None
    actual_hours: float = 0.0
    is_subtask: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Optional expanded fields - will be populated if relationships are loaded
    project_name: Optional[str] = None
    assignee_username: Optional[str] = None
    assignee_name: Optional[str] = None
    created_by_username: Optional[str] = None
    created_by_name: Optional[str] = None
    sprint_name: Optional[str] = None
    time_logs: Optional[List[Dict[str, Any]]] = None
    active_timer: Optional[Dict[str, Any]] = None
    subtasks: Optional[List["TaskResponse"]] = None  # List of subtasks

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_expansions(cls, task):
        """Create response with expanded relationship data"""
        data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "story_points": task.story_points,
            "estimated_hours": task.estimated_hours,
            "due_date": task.due_date,
            "is_subtask": task.is_subtask,
            "project_id": task.project_id,
            "sprint_id": task.sprint_id,
            "assignee_id": task.assignee_id,
            "created_by_id": task.created_by_id,
            "parent_task_id": task.parent_task_id,
            "actual_hours": task.actual_hours,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
        
        # Add expanded data if relationships are loaded
        if hasattr(task, 'project') and task.project:
            data["project_name"] = task.project.name
            
        if hasattr(task, 'assignee') and task.assignee:
            data["assignee_username"] = task.assignee.username
            if task.assignee.first_name and task.assignee.last_name:
                data["assignee_name"] = f"{task.assignee.first_name} {task.assignee.last_name}"
            elif task.assignee.first_name:
                data["assignee_name"] = task.assignee.first_name
                
        if hasattr(task, 'created_by') and task.created_by:
            data["created_by_username"] = task.created_by.username
            if task.created_by.first_name and task.created_by.last_name:
                data["created_by_name"] = f"{task.created_by.first_name} {task.created_by.last_name}"
            elif task.created_by.first_name:
                data["created_by_name"] = task.created_by.first_name
                
        if hasattr(task, 'sprint') and task.sprint:
            data["sprint_name"] = task.sprint.name
            
        return cls(**data)
