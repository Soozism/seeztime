"""
Tag management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.tag import Tag
from app.models.enums import UserRole
from app.schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter()

@router.get("/", response_model=List[TagResponse])
def get_tags(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tags, optionally filtered by category"""
    query = db.query(Tag)
    if category:
        query = query.filter(Tag.category == category)
    tags = query.all()
    return tags

@router.post("/", response_model=TagResponse)
def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new tag"""
    # Only admins and project managers can create tags
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if tag name already exists
    existing = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tag name already exists")
    
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a tag"""
    # Only admins and project managers can update tags
    if current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    # Check if new name already exists (if being updated)
    if tag_update.name and tag_update.name != tag.name:
        existing = db.query(Tag).filter(Tag.name == tag_update.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tag name already exists")
    
    # Update tag data
    for key, value in tag_update.dict(exclude_unset=True).items():
        setattr(tag, key, value)
    
    db.commit()
    db.refresh(tag)
    return tag

@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a tag"""
    # Only admins can delete tags
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted successfully"}

@router.get("/categories/", response_model=List[str])
def get_tag_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all unique tag categories"""
    categories = db.query(Tag.category).filter(Tag.category.isnot(None)).distinct().all()
    return [category[0] for category in categories if category[0]]
