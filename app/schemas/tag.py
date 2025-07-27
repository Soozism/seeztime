"""
Tag schemas for request/response validation
"""

from pydantic import BaseModel
from typing import Optional

class TagBase(BaseModel):
    name: str
    color: str = "#007bff"
    description: Optional[str] = None
    category: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class TagResponse(TagBase):
    id: int

    class Config:
        from_attributes = True
