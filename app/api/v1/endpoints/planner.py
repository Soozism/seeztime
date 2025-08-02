# FastAPI endpoints for personal planner (events and todos)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models import PlannerEvent, PersonalTodo, User
from app.schemas.planner_event import (
    PlannerEventCreate, PlannerEventUpdate, PlannerEventResponse,
    PersonalTodoCreate, PersonalTodoUpdate, PersonalTodoResponse
)

router = APIRouter()

# Permission helper: only owner can access
def can_access_planner(user: User, target_user_id: int) -> bool:
    return user.id == target_user_id

# Event endpoints
@router.get("/events", response_model=List[PlannerEventResponse])
def get_my_events(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    events = db.query(PlannerEvent).filter(PlannerEvent.user_id == current_user.id).all()
    return events

@router.post("/events", response_model=PlannerEventResponse)
def create_event(event_in: PlannerEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = PlannerEvent(**event_in.dict(), user_id=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.put("/events/{event_id}", response_model=PlannerEventResponse)
def update_event(event_id: int, event_in: PlannerEventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = db.query(PlannerEvent).filter(PlannerEvent.id == event_id, PlannerEvent.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    for field, value in event_in.dict(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    event = db.query(PlannerEvent).filter(PlannerEvent.id == event_id, PlannerEvent.user_id == current_user.id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    db.commit()
    return

# Personal todo endpoints
@router.get("/todos", response_model=List[PersonalTodoResponse])
def get_my_todos(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    todos = db.query(PersonalTodo).filter(PersonalTodo.user_id == current_user.id).all()
    return todos

@router.post("/todos", response_model=PersonalTodoResponse)
def create_todo(todo_in: PersonalTodoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    todo = PersonalTodo(**todo_in.dict(), user_id=current_user.id)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@router.put("/todos/{todo_id}", response_model=PersonalTodoResponse)
def update_todo(todo_id: int, todo_in: PersonalTodoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    todo = db.query(PersonalTodo).filter(PersonalTodo.id == todo_id, PersonalTodo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for field, value in todo_in.dict(exclude_unset=True).items():
        setattr(todo, field, value)
    db.commit()
    db.refresh(todo)
    return todo

@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    todo = db.query(PersonalTodo).filter(PersonalTodo.id == todo_id, PersonalTodo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return
