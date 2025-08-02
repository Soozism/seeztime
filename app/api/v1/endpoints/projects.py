"""
Project management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.sprint import Sprint
from app.models.milestone import Milestone
from app.models.time_log import TimeLog
from app.models.team import Team
from app.models.enums import TaskStatus, SprintStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailedResponse

router = APIRouter()

@router.get("/", response_model=List[ProjectResponse])
def get_projects(
    skip: int = 0,
    limit: int = 100,
    show_closed: bool = False,
    status: str = None,
    expand: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all projects with enhanced filtering and optional expanded details
    
    Parameters:
    - show_closed: If True, includes finished/archived projects. If False, shows only active projects
    - status: Filter by specific project status (active, completed, archived)
    - expand: Include expanded details like creator info and time tracking
    
    Returns projects with task counts and total spent time
    """
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    # Base query based on user role
    if current_user.role.value == 'admin':
        # Admins can see all projects
        if expand:
            query = db.query(Project).options(joinedload(Project.created_by))
        else:
            query = db.query(Project)
    elif current_user.role.value == 'project_manager':
        # Project managers can VIEW all projects but can only EDIT their own
        if expand:
            query = db.query(Project).options(joinedload(Project.created_by))
        else:
            query = db.query(Project)
    elif current_user.role.value == 'team_leader':
        # Team leaders can see projects assigned to their teams
        if expand:
            query = db.query(Project).join(Team.projects).filter(
                Team.team_leader_id == current_user.id
            ).distinct().options(joinedload(Project.created_by))
        else:
            query = db.query(Project).join(Team.projects).filter(Team.team_leader_id == current_user.id).distinct()
    else:
        # Employees can only see projects with tasks assigned to them
        if expand:
            query = db.query(Project).join(Task).filter(
                Task.assignee_id == current_user.id
            ).distinct().options(joinedload(Project.created_by))
        else:
            query = db.query(Project).join(Task).filter(Task.assignee_id == current_user.id).distinct()
    
    # Apply status filter
    if not show_closed and not status:
        from app.models.enums import ProjectStatus
        query = query.filter(Project.status == ProjectStatus.ACTIVE)
    elif status:
        query = query.filter(Project.status == status)
    # If show_closed=True and no specific status, show all projects including COMPLETED and ARCHIVED
    
    projects = query.offset(skip).limit(limit).all()
    
    # Convert to response objects with expansions if requested
    def calculate_completion_percentage(project):
        try:
            project_estimated_time = getattr(project, 'estimated_time', None)
            if project_estimated_time is None or project_estimated_time == 0:
                return 0.0
            sprints = db.query(Sprint).filter(Sprint.project_id == project.id).all()
            sprint_percentages = []
            for sprint in sprints:
                sprint_estimated_time = getattr(sprint, 'estimated_time', None)
                if sprint_estimated_time is None or sprint_estimated_time == 0:
                    continue
                sprint_tasks = db.query(Task).filter(Task.sprint_id == sprint.id).all()
                total_sprint_tasks = len(sprint_tasks)
                if total_sprint_tasks == 0:
                    continue
                done_sprint_tasks = sum(1 for t in sprint_tasks if t.status == TaskStatus.DONE)
                sprint_contribution = (sprint_estimated_time / project_estimated_time) * (done_sprint_tasks / total_sprint_tasks)
                sprint_percentages.append(sprint_contribution)
            if sprint_percentages:
                return round(sum(sprint_percentages) * 100, 2)
            else:
                return 0.0
        except Exception:
            return 0.0

    if expand:
        result = []
        for project in projects:
            total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
            done_tasks = db.query(func.count(Task.id)).filter(
                Task.project_id == project.id, 
                Task.status == TaskStatus.DONE
            ).scalar() or 0
            total_spent_hours = db.query(func.coalesce(func.sum(TimeLog.hours), 0)).join(
                Task, TimeLog.task_id == Task.id
            ).filter(Task.project_id == project.id).scalar() or 0
            completion_percentage = calculate_completion_percentage(project)
            project_response = ProjectResponse.from_orm_with_expansions(
                project, total_tasks, done_tasks, float(total_spent_hours), completion_percentage
            )
            result.append(project_response)
        return result
    else:
        result = []
        for project in projects:
            total_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
            done_tasks = db.query(func.count(Task.id)).filter(
                Task.project_id == project.id, 
                Task.status == TaskStatus.DONE
            ).scalar() or 0
            total_spent_hours = db.query(func.coalesce(func.sum(TimeLog.hours), 0)).join(
                Task, TimeLog.task_id == Task.id
            ).filter(Task.project_id == project.id).scalar() or 0
            completion_percentage = calculate_completion_percentage(project)
            project_data = ProjectResponse(
                id=project.id,
                name=project.name,
                description=project.description,
                start_date=project.start_date,
                end_date=project.end_date,
                status=project.status,
                created_by_id=project.created_by_id,
                created_at=project.created_at,
                updated_at=project.updated_at,
                total_tasks=total_tasks,
                done_tasks=done_tasks,
                total_spent_hours=float(total_spent_hours)
            )
            if hasattr(project_data, 'completion_percentage'):
                project_data.completion_percentage = completion_percentage
            else:
                project_data = project_data.dict()
                project_data['completion_percentage'] = completion_percentage
            result.append(project_data)
        return result

@router.get("/{project_id}", response_model=ProjectDetailedResponse)
def get_project(
    project_id: int,
    expand: bool = True,
    include_details: bool = True,
    include_users: bool = True,
    sprint_done: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get project by ID with comprehensive statistics and optional detailed lists"""
    from sqlalchemy.orm import joinedload
    from sqlalchemy import func
    
    if expand:
        project = db.query(Project).options(
            joinedload(Project.created_by)
        ).filter(Project.id == project_id).first()
    else:
        project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate task statistics
    task_stats = db.query(
        func.count(Task.id).label('total'),
        func.count(func.nullif(Task.status != TaskStatus.TODO, True)).label('todo'),
        func.count(func.nullif(Task.status != TaskStatus.IN_PROGRESS, True)).label('in_progress'),
        func.count(func.nullif(Task.status != TaskStatus.REVIEW, True)).label('review'),
        func.count(func.nullif(Task.status != TaskStatus.DONE, True)).label('done')
    ).filter(Task.project_id == project_id).first()
    
    total_tasks = task_stats.total or 0
    todo_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project_id, Task.status == TaskStatus.TODO).scalar() or 0
    in_progress_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project_id, Task.status == TaskStatus.IN_PROGRESS).scalar() or 0
    review_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project_id, Task.status == TaskStatus.REVIEW).scalar() or 0
    done_tasks = db.query(func.count(Task.id)).filter(Task.project_id == project_id, Task.status == TaskStatus.DONE).scalar() or 0
    
    # Calculate sprint statistics
    total_sprints = db.query(func.count(Sprint.id)).filter(Sprint.project_id == project_id).scalar() or 0
    planned_sprints = db.query(func.count(Sprint.id)).filter(Sprint.project_id == project_id, Sprint.status == SprintStatus.PLANNED).scalar() or 0
    active_sprints = db.query(func.count(Sprint.id)).filter(Sprint.project_id == project_id, Sprint.status == SprintStatus.ACTIVE).scalar() or 0
    completed_sprints = db.query(func.count(Sprint.id)).filter(Sprint.project_id == project_id, Sprint.status == SprintStatus.COMPLETED).scalar() or 0
    
    # Calculate sprint estimated hours
    total_sprint_hours = db.query(func.coalesce(func.sum(Sprint.estimated_hours), 0)).filter(Sprint.project_id == project_id).scalar() or 0
    planned_sprint_hours = db.query(func.coalesce(func.sum(Sprint.estimated_hours), 0)).filter(
        Sprint.project_id == project_id, Sprint.status == SprintStatus.PLANNED
    ).scalar() or 0
    active_sprint_hours = db.query(func.coalesce(func.sum(Sprint.estimated_hours), 0)).filter(
        Sprint.project_id == project_id, Sprint.status == SprintStatus.ACTIVE
    ).scalar() or 0
    completed_sprint_hours = db.query(func.coalesce(func.sum(Sprint.estimated_hours), 0)).filter(
        Sprint.project_id == project_id, Sprint.status == SprintStatus.COMPLETED
    ).scalar() or 0
    
    # Calculate milestone statistics
    total_milestones = db.query(func.count(Milestone.id)).filter(Milestone.project_id == project_id).scalar() or 0
    completed_milestones = db.query(func.count(Milestone.id)).filter(
        Milestone.project_id == project_id, 
        Milestone.completed_at.isnot(None)
    ).scalar() or 0
    pending_milestones = total_milestones - completed_milestones
    
    # Calculate milestone estimated hours
    total_milestone_hours = db.query(func.coalesce(func.sum(Milestone.estimated_hours), 0)).filter(Milestone.project_id == project_id).scalar() or 0
    completed_milestone_hours = db.query(func.coalesce(func.sum(Milestone.estimated_hours), 0)).filter(
        Milestone.project_id == project_id, Milestone.completed_at.isnot(None)
    ).scalar() or 0
    pending_milestone_hours = total_milestone_hours - completed_milestone_hours
    
    # Calculate phase statistics
    from app.models.phase import Phase
    total_phases = db.query(func.count(Phase.id)).filter(Phase.project_id == project_id).scalar() or 0
    total_phase_hours = db.query(func.coalesce(func.sum(Phase.estimated_hours), 0)).filter(Phase.project_id == project_id).scalar() or 0
    
    # Calculate percentages
    task_summary = {
        "total": total_tasks,
        "todo": todo_tasks,
        "in_progress": in_progress_tasks,
        "review": review_tasks,
        "done": done_tasks,
        "todo_percentage": round((todo_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        "in_progress_percentage": round((in_progress_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        "review_percentage": round((review_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        "done_percentage": round((done_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2)
    }
    
    sprint_summary = {
        "total": total_sprints,
        "planned": planned_sprints,
        "active": active_sprints,
        "completed": completed_sprints,
        "planned_percentage": round((planned_sprints / total_sprints * 100) if total_sprints > 0 else 0, 2),
        "active_percentage": round((active_sprints / total_sprints * 100) if total_sprints > 0 else 0, 2),
        "completed_percentage": round((completed_sprints / total_sprints * 100) if total_sprints > 0 else 0, 2),
        "total_estimated_hours": round(total_sprint_hours, 2),
        "planned_estimated_hours": round(planned_sprint_hours, 2),
        "active_estimated_hours": round(active_sprint_hours, 2),
        "completed_estimated_hours": round(completed_sprint_hours, 2)
    }
    
    milestone_summary = {
        "total": total_milestones,
        "pending": pending_milestones,
        "completed": completed_milestones,
        "pending_percentage": round((pending_milestones / total_milestones * 100) if total_milestones > 0 else 0, 2),
        "completed_percentage": round((completed_milestones / total_milestones * 100) if total_milestones > 0 else 0, 2),
        "total_estimated_hours": round(total_milestone_hours, 2),
        "pending_estimated_hours": round(pending_milestone_hours, 2),
        "completed_estimated_hours": round(completed_milestone_hours, 2)
    }
    
    phase_summary = {
        "total": total_phases,
        "total_estimated_hours": round(total_phase_hours, 2)
    }
    
    # Calculate user statistics if requested
    users_summary = None
    if include_users:
        from sqlalchemy import func
        
        # Get all users who have tasks assigned in this project
        project_users = db.query(User).join(Task, Task.assignee_id == User.id).filter(
            Task.project_id == project_id
        ).distinct().all()
        
        users_stats = []
        total_project_hours = 0
        total_project_story_points = 0
        
        for user in project_users:
            # Get time statistics for this user
            total_hours = db.query(func.coalesce(func.sum(TimeLog.hours), 0)).join(
                Task, TimeLog.task_id == Task.id
            ).filter(
                TimeLog.user_id == user.id,
                Task.project_id == project_id
            ).scalar() or 0
            
            # Get story points for this user
            total_story_points_query = db.query(func.coalesce(func.sum(Task.story_points), 0)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project_id
            ).scalar() or 0
            
            # Get task counts for this user
            tasks_completed = db.query(func.count(Task.id)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project_id,
                Task.status == TaskStatus.DONE
            ).scalar() or 0
            
            tasks_in_progress = db.query(func.count(Task.id)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project_id,
                Task.status == TaskStatus.IN_PROGRESS
            ).scalar() or 0
            
            tasks_total = db.query(func.count(Task.id)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project_id
            ).scalar() or 0
            
            full_name = None
            if user.first_name and user.last_name:
                full_name = f"{user.first_name} {user.last_name}"
            elif user.first_name:
                full_name = user.first_name
            
            user_data = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": full_name,
                "total_hours": float(total_hours),
                "total_story_points": int(total_story_points_query),
                "tasks_completed": int(tasks_completed),
                "tasks_in_progress": int(tasks_in_progress),
                "tasks_total": int(tasks_total)
            }
            users_stats.append(user_data)
            total_project_hours += float(total_hours)
            total_project_story_points += int(total_story_points_query)
        
        users_summary = {
            "total_project_hours": round(total_project_hours, 2),
            "total_project_story_points": total_project_story_points,
            "active_users_count": len(users_stats),
            "users_stats": users_stats
        }
    
    # Calculate project completion percentage based on sprints, estimated times, and done tasks
    project_completion_percentage = 0.0
    try:
        # Get project estimated time
        project_estimated_time = getattr(project, 'estimated_hours', None)
        
        if project_estimated_time is None or project_estimated_time == 0:
            project_completion_percentage = 0.0
            print(f"Sprinthas no estimated time")
        else:
            sprints = db.query(Sprint).filter(Sprint.project_id == project_id).all()
            sprint_percentages = []
            for sprint in sprints:
                sprint_estimated_time = getattr(sprint, 'estimated_hours', None)
                
                if sprint_estimated_time is None or sprint_estimated_time == 0:
                    
                    continue
                sprint_tasks = db.query(Task).filter(Task.sprint_id == sprint.id).all()
                total_sprint_tasks = len(sprint_tasks)
                if total_sprint_tasks == 0:
                    continue
                done_sprint_tasks = sum(1 for t in sprint_tasks if t.status == TaskStatus.DONE)
                # Calculate sprint's contribution to project completion
                sprint_contribution = (sprint_estimated_time / project_estimated_time) * (done_sprint_tasks / total_sprint_tasks)
                sprint_percentages.append(sprint_contribution)
            if sprint_percentages:
                project_completion_percentage = round(sum(sprint_percentages) * 100, 2)
            else:
                project_completion_percentage = 0.0
    except Exception:
        project_completion_percentage = 0.0

    # Prepare base response data
    response_data = {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "estimated_hours": project.estimated_hours,
        "start_date": project.start_date,
        "end_date": project.end_date,
        "status": project.status,
        "created_by_id": project.created_by_id,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "task_summary": task_summary,
        "sprint_summary": sprint_summary,
        "milestone_summary": milestone_summary,
        "phase_summary": phase_summary,
        "users_summary": users_summary,
        "completion_percentage": project_completion_percentage
    }
    
    # Add expanded user data if available
    if expand and hasattr(project, 'created_by') and project.created_by:
        response_data["created_by_username"] = project.created_by.username
        if project.created_by.first_name and project.created_by.last_name:
            response_data["created_by_name"] = f"{project.created_by.first_name} {project.created_by.last_name}"
        elif project.created_by.first_name:
            response_data["created_by_name"] = project.created_by.first_name
    
    # Include detailed lists if requested
    if include_details:
        # Get detailed task information
        tasks_query = db.query(Task).options(
            joinedload(Task.assignee),
            joinedload(Task.sprint)
        ).filter(Task.project_id == project_id)

        # Apply sprint completion filter
        if sprint_done:
            tasks_query = tasks_query.filter(Task.sprint_id.isnot(None)).filter(
                Task.sprint.has(Sprint.status == SprintStatus.COMPLETED)
            )
        else:
            tasks_query = tasks_query.filter(
                (Task.sprint_id.is_(None)) | (Task.sprint.has(Sprint.status != SprintStatus.COMPLETED))
            )

        # Order newest first then higher priority
        tasks_query = tasks_query.order_by(Task.created_at.desc(), Task.priority.desc())

        tasks = tasks_query.all()
        
        task_details = []
        for task in tasks:
            task_detail = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value,
                "story_points": task.story_points,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "due_date": task.due_date,
                "assignee_name": f"{task.assignee.first_name} {task.assignee.last_name}" if task.assignee and task.assignee.first_name else None,
                "assignee_username": task.assignee.username if task.assignee else None,
                "sprint_name": task.sprint.name if task.sprint else None,
                "is_subtask": task.is_subtask
            }
            task_details.append(task_detail)
        
        # Get detailed sprint information  
        sprints = db.query(Sprint).filter(Sprint.project_id == project_id).all()
        sprint_details = []
        for sprint in sprints:
            sprint_task_count = db.query(func.count(Task.id)).filter(Task.sprint_id == sprint.id).scalar() or 0
            sprint_detail = {
                "id": sprint.id,
                "name": sprint.name,
                "description": sprint.description,
                "status": sprint.status.value,
                "estimated_hours": sprint.estimated_hours,
                "start_date": sprint.start_date,
                "end_date": sprint.end_date,
                "created_at": sprint.created_at,
                "updated_at": sprint.updated_at,
                "task_count": sprint_task_count
            }
            sprint_details.append(sprint_detail)
        
        # Get detailed milestone information
        milestones = db.query(Milestone).filter(Milestone.project_id == project_id).all()
        milestone_details = []
        for milestone in milestones:
            # Count sprints associated with this milestone
            sprint_count = db.query(func.count(Sprint.id)).filter(Sprint.milestone_id == milestone.id).scalar() or 0
            milestone_detail = {
                "id": milestone.id,
                "name": milestone.name,
                "description": milestone.description,
                "estimated_hours": milestone.estimated_hours,
                "due_date": milestone.due_date,
                "completed_at": milestone.completed_at,
                "created_at": milestone.created_at,
                "updated_at": milestone.updated_at,
                "sprint_count": sprint_count,
                "is_completed": milestone.completed_at is not None
            }
            milestone_details.append(milestone_detail)
        
        # Get detailed phase information
        phases = db.query(Phase).filter(Phase.project_id == project_id).all()
        phase_details = []
        for phase in phases:
            # Count milestones associated with this phase
            milestone_count = db.query(func.count(Milestone.id)).filter(Milestone.phase_id == phase.id).scalar() or 0
            phase_detail = {
                "id": phase.id,
                "name": phase.name,
                "description": phase.description,
                "estimated_hours": phase.estimated_hours,
                "start_date": phase.start_date,
                "end_date": phase.end_date,
                "created_at": phase.created_at,
                "updated_at": phase.updated_at,
                "milestone_count": milestone_count
            }
            phase_details.append(phase_detail)
        
        response_data["tasks"] = task_details
        response_data["sprints"] = sprint_details
        response_data["milestones"] = milestone_details
        response_data["phases"] = phase_details
    
    return ProjectDetailedResponse(**response_data)

@router.post("/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create new project"""
    db_project = Project(
        **project.dict(),
        created_by_id=current_user.id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}

@router.patch("/{project_id}/close")
def close_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Close a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions - only project creator or admin can close projects
    if current_user.role.value != 'admin' and project.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if project is already closed
    from app.models.enums import ProjectStatus
    if project.status == ProjectStatus.ARCHIVED:
        raise HTTPException(status_code=400, detail="Project is already closed")
    
    project.status = ProjectStatus.ARCHIVED
    db.commit()
    db.refresh(project)
    return project

@router.patch("/{project_id}/reopen")
def reopen_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reopen a closed project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check permissions - only project creator or admin can reopen projects
    if current_user.role.value != 'admin' and project.created_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if project is already active
    from app.models.enums import ProjectStatus
    if project.status == ProjectStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Project is already active")
    
    project.status = ProjectStatus.ACTIVE
    db.commit()
    db.refresh(project)
    return project

@router.get("/{project_id}/tasks")
def get_project_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    sprint_done: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all tasks for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks_query = db.query(Task).filter(Task.project_id == project_id)

    # Apply sprint completion filter
    if sprint_done:
        tasks_query = tasks_query.filter(Task.sprint_id.isnot(None)).filter(
            Task.sprint.has(Sprint.status == SprintStatus.COMPLETED)
        )
    else:
        tasks_query = tasks_query.filter(
            (Task.sprint_id.is_(None)) | (Task.sprint.has(Sprint.status != SprintStatus.COMPLETED))
        )

    # Order newest first then higher priority
    tasks_query = tasks_query.order_by(Task.created_at.desc(), Task.priority.desc())

    tasks = tasks_query.offset(skip).limit(limit).all()
    return tasks

@router.get("/{project_id}/sprints")
def get_project_sprints(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all sprints for a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sprints = db.query(Sprint).filter(Sprint.project_id == project_id).offset(skip).limit(limit).all()
    return sprints

@router.get("/{project_id}/phases")
def get_project_phases(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    include_milestones: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all phases for a project with optional milestone details"""
    from app.models.phase import Phase
    from sqlalchemy.orm import joinedload
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    query = db.query(Phase).filter(Phase.project_id == project_id)
    
    if include_milestones:
        query = query.options(joinedload(Phase.milestones))
    
    phases = query.offset(skip).limit(limit).all()
    
    if include_milestones:
        from app.schemas.phase import PhaseResponse
        return [PhaseResponse.from_orm_with_expansions(phase, include_project_name=False) for phase in phases]
    else:
        return phases

@router.get("/{project_id}/users")
def get_project_users(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all users working on a project with their statistics"""
    from sqlalchemy import func
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get all users who have tasks assigned in this project
    project_users = db.query(User).join(Task, Task.assignee_id == User.id).filter(
        Task.project_id == project_id
    ).distinct().all()
    
    users_stats = []
    total_project_hours = 0
    total_project_story_points = 0
    
    for user in project_users:
        # Get time statistics for this user
        total_hours = db.query(func.coalesce(func.sum(TimeLog.hours), 0)).join(
            Task, TimeLog.task_id == Task.id
        ).filter(
            TimeLog.user_id == user.id,
            Task.project_id == project_id
        ).scalar() or 0
        
        # Get story points for this user
        total_story_points_query = db.query(func.coalesce(func.sum(Task.story_points), 0)).filter(
            Task.assignee_id == user.id,
            Task.project_id == project_id
        ).scalar() or 0
        
        # Get task counts for this user
        tasks_completed = db.query(func.count(Task.id)).filter(
            Task.assignee_id == user.id,
            Task.project_id == project_id,
            Task.status == TaskStatus.DONE
        ).scalar() or 0
        
        tasks_in_progress = db.query(func.count(Task.id)).filter(
            Task.assignee_id == user.id,
            Task.project_id == project_id,
            Task.status == TaskStatus.IN_PROGRESS
        ).scalar() or 0
        
        tasks_todo = db.query(func.count(Task.id)).filter(
            Task.assignee_id == user.id,
            Task.project_id == project_id,
            Task.status == TaskStatus.TODO
        ).scalar() or 0
        
        tasks_review = db.query(func.count(Task.id)).filter(
            Task.assignee_id == user.id,
            Task.project_id == project_id,
            Task.status == TaskStatus.REVIEW
        ).scalar() or 0
        
        tasks_total = db.query(func.count(Task.id)).filter(
            Task.assignee_id == user.id,
            Task.project_id == project_id
        ).scalar() or 0
        
        full_name = None
        if user.first_name and user.last_name:
            full_name = f"{user.first_name} {user.last_name}"
        elif user.first_name:
            full_name = user.first_name
        
        user_data = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": full_name,
            "email": user.email,
            "role": user.role.value,
            "total_hours": float(total_hours),
            "total_story_points": int(total_story_points_query),
            "tasks_completed": int(tasks_completed),
            "tasks_in_progress": int(tasks_in_progress),
            "tasks_todo": int(tasks_todo),
            "tasks_review": int(tasks_review),
            "tasks_total": int(tasks_total)
        }
        users_stats.append(user_data)
        total_project_hours += float(total_hours)
        total_project_story_points += int(total_story_points_query)
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_project_hours": round(total_project_hours, 2),
        "total_project_story_points": total_project_story_points,
        "active_users_count": len(users_stats),
        "users_stats": users_stats
    }
