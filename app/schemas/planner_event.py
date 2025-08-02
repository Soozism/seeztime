# Schemas for PlannerEvent and PersonalTodo
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PlannerEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: Optional[str] = None  # e.g., meeting, hobby, etc.

class PlannerEventCreate(PlannerEventBase):
    pass

class PlannerEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    event_type: Optional[str] = None

class PlannerEventResponse(PlannerEventBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        orm_mode = True

# Personal Todo schemas
class PersonalTodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: bool = False

class PersonalTodoCreate(PersonalTodoBase):
    pass

class PersonalTodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None

class PersonalTodoResponse(PersonalTodoBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    class Config:
        orm_mode = True
