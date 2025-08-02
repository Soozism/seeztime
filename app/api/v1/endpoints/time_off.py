"""
Time Off management API endpoints
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.enums import UserRole, TimeOffStatus
from app.models.working_hours import TimeOff
from app.schemas.working_hours import TimeOffCreate, TimeOffUpdate, TimeOffResponse

router = APIRouter()

def can_manage_time_off(user: User, target_user_id: int = None) -> bool:
    """Check if user can manage time off requests"""
    if user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        return True
    if target_user_id and user.id == target_user_id:
        return True  # Users can manage their own time off
    return False

def can_approve_time_off(user: User) -> bool:
    """Check if user can approve time off requests"""
    return user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]

@router.get("/time-off", response_model=List[TimeOffResponse])
def get_time_off_requests(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    status_filter: Optional[TimeOffStatus] = Query(None, description="Filter by status"),
    start_date: Optional[date] = Query(None, description="Filter from start date"),
    end_date: Optional[date] = Query(None, description="Filter to end date"),
    expand: bool = Query(False, description="Include user names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time off requests"""
    query = db.query(TimeOff)
    
    # Apply filters
    if user_id:
        if not can_manage_time_off(current_user, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to view this user's time off requests"
            )
        query = query.filter(TimeOff.user_id == user_id)
    elif current_user.role not in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Non-privileged users can only see their own
        query = query.filter(TimeOff.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(TimeOff.status == status_filter)
    
    if start_date:
        query = query.filter(TimeOff.start_date >= start_date)
    
    if end_date:
        query = query.filter(TimeOff.end_date <= end_date)
    
    time_off_requests = query.order_by(TimeOff.start_date.desc()).all()
    
    if expand:
        result = []
        for request in time_off_requests:
            request_dict = TimeOffResponse.from_orm(request).dict()
            request_dict['user_name'] = request.user.username
            if request.approved_by:
                request_dict['approved_by_name'] = request.approved_by.username
            # Calculate days count
            days_count = (request.end_date - request.start_date).days + 1
            request_dict['days_count'] = days_count
            result.append(TimeOffResponse(**request_dict))
        return result
    
    return [TimeOffResponse.from_orm(request) for request in time_off_requests]


@router.post("/time-off", response_model=TimeOffResponse)
def create_time_off_request(
    time_off_data: TimeOffCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new time off request"""
    # Determine target user for the time-off request
    if current_user.role in [UserRole.ADMIN, UserRole.PROJECT_MANAGER]:
        # Admin/PM can specify another user; default to themselves if not provided
        user_id = time_off_data.user_id or current_user.id
    else:
        # Regular users can only create requests for themselves
        user_id = current_user.id
    
    # Validate dates
    if time_off_data.start_date > time_off_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    if time_off_data.start_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create time off requests for past dates"
        )
    
    # Check for overlapping requests
    overlapping = db.query(TimeOff).filter(
        and_(
            TimeOff.user_id == user_id,
            TimeOff.status.in_([TimeOffStatus.PENDING, TimeOffStatus.APPROVED]),
            or_(
                and_(TimeOff.start_date <= time_off_data.start_date, TimeOff.end_date >= time_off_data.start_date),
                and_(TimeOff.start_date <= time_off_data.end_date, TimeOff.end_date >= time_off_data.end_date),
                and_(TimeOff.start_date >= time_off_data.start_date, TimeOff.end_date <= time_off_data.end_date)
            )
        )
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping time off request exists"
        )
    
    db_time_off = TimeOff(
        user_id=user_id,
        start_date=time_off_data.start_date,
        end_date=time_off_data.end_date,
        reason=time_off_data.reason,
        status=TimeOffStatus.PENDING
    )
    
    db.add(db_time_off)
    db.commit()
    db.refresh(db_time_off)
    
    return TimeOffResponse.from_orm(db_time_off)


@router.get("/time-off/{time_off_id}", response_model=TimeOffResponse)
def get_time_off_by_id(
    time_off_id: int,
    expand: bool = Query(False, description="Include user names"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get time off request by ID"""
    time_off = db.query(TimeOff).filter(TimeOff.id == time_off_id).first()
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time off request not found"
        )
    
    if not can_manage_time_off(current_user, time_off.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this time off request"
        )
    
    if expand:
        request_dict = TimeOffResponse.from_orm(time_off).dict()
        request_dict['user_name'] = time_off.user.username
        if time_off.approved_by:
            request_dict['approved_by_name'] = time_off.approved_by.username
        days_count = (time_off.end_date - time_off.start_date).days + 1
        request_dict['days_count'] = days_count
        return TimeOffResponse(**request_dict)
    
    return TimeOffResponse.from_orm(time_off)


@router.put("/time-off/{time_off_id}", response_model=TimeOffResponse)
def update_time_off_request(
    time_off_id: int,
    time_off_update: TimeOffUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update time off request"""
    time_off = db.query(TimeOff).filter(TimeOff.id == time_off_id).first()
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time off request not found"
        )
    
    if not can_manage_time_off(current_user, time_off.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this time off request"
        )
    
    # Only allow users to edit their own pending requests
    if current_user.id == time_off.user_id and time_off.status != TimeOffStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only edit pending time off requests"
        )
    
    # Update fields
    for field, value in time_off_update.dict(exclude_unset=True).items():
        setattr(time_off, field, value)
    
    # Validate dates if they were updated
    if time_off.start_date > time_off.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    db.commit()
    db.refresh(time_off)
    
    return TimeOffResponse.from_orm(time_off)


@router.post("/time-off/{time_off_id}/approve")
def approve_time_off_request(
    time_off_id: int,
    approval_notes: Optional[str] = Query(None, description="Approval notes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Approve time off request"""
    if not can_approve_time_off(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to approve time off requests"
        )
    
    time_off = db.query(TimeOff).filter(TimeOff.id == time_off_id).first()
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time off request not found"
        )
    
    if time_off.status != TimeOffStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only approve pending requests"
        )
    
    time_off.status = TimeOffStatus.APPROVED
    time_off.approved_by_id = current_user.id
    from datetime import datetime
    time_off.approved_at = datetime.utcnow()
    if approval_notes:
        time_off.approval_notes = approval_notes
    
    db.commit()
    
    return {"message": "Time off request approved successfully"}


@router.post("/time-off/{time_off_id}/reject")
def reject_time_off_request(
    time_off_id: int,
    rejection_reason: str = Query(..., description="Reason for rejection"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reject time off request"""
    if not can_approve_time_off(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to reject time off requests"
        )
    
    time_off = db.query(TimeOff).filter(TimeOff.id == time_off_id).first()
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time off request not found"
        )
    
    if time_off.status != TimeOffStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only reject pending requests"
        )
    
    time_off.status = TimeOffStatus.REJECTED
    time_off.approved_by_id = current_user.id
    from datetime import datetime
    time_off.approved_at = datetime.utcnow()
    time_off.approval_notes = rejection_reason
    
    db.commit()
    
    return {"message": "Time off request rejected successfully"}


@router.delete("/time-off/{time_off_id}")
def delete_time_off_request(
    time_off_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete time off request"""
    time_off = db.query(TimeOff).filter(TimeOff.id == time_off_id).first()
    if not time_off:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time off request not found"
        )
    
    if not can_manage_time_off(current_user, time_off.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this time off request"
        )
    
    # Only allow deletion of pending requests or by admin/PM
    if current_user.id == time_off.user_id and time_off.status != TimeOffStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete pending time off requests"
        )
    
    db.delete(time_off)
    db.commit()
    
    return {"message": "Time off request deleted successfully"}
