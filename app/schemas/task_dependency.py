"""
Task Dependency schemas for request/response validation
"""

from pydantic import BaseModel

class TaskDependencyBase(BaseModel):
    task_id: int
    depends_on_task_id: int

class TaskDependencyCreate(TaskDependencyBase):
    pass

class TaskDependencyResponse(TaskDependencyBase):
    id: int

    class Config:
        from_attributes = True
