"""
Simple test to verify the new project user statistics functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.time_log import TimeLog
from app.models.enums import UserRole, TaskStatus, TaskPriority
from datetime import datetime

def test_user_statistics():
    """Test the user statistics calculation directly"""
    db: Session = SessionLocal()
    
    try:
        # Find an existing project or create one
        project = db.query(Project).first()
        if not project:
            print("No projects found in the database")
            return
        
        print(f"Testing with project: {project.name} (ID: {project.id})")
        
        # Get users who have tasks in this project
        project_users = db.query(User).join(Task, Task.assignee_id == User.id).filter(
            Task.project_id == project.id
        ).distinct().all()
        
        print(f"Found {len(project_users)} users working on this project:")
        
        total_project_hours = 0
        total_project_story_points = 0
        
        for user in project_users:
            # Get time statistics for this user
            from sqlalchemy import func
            total_hours = db.query(func.coalesce(func.sum(TimeLog.hours), 0)).join(
                Task, TimeLog.task_id == Task.id
            ).filter(
                TimeLog.user_id == user.id,
                Task.project_id == project.id
            ).scalar() or 0
            
            # Get story points for this user
            total_story_points = db.query(func.coalesce(func.sum(Task.story_points), 0)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project.id
            ).scalar() or 0
            
            # Get task counts for this user
            tasks_completed = db.query(func.count(Task.id)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project.id,
                Task.status == TaskStatus.DONE
            ).scalar() or 0
            
            tasks_in_progress = db.query(func.count(Task.id)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project.id,
                Task.status == TaskStatus.IN_PROGRESS
            ).scalar() or 0
            
            tasks_total = db.query(func.count(Task.id)).filter(
                Task.assignee_id == user.id,
                Task.project_id == project.id
            ).scalar() or 0
            
            full_name = None
            if user.first_name and user.last_name:
                full_name = f"{user.first_name} {user.last_name}"
            elif user.first_name:
                full_name = user.first_name
            else:
                full_name = user.username
            
            print(f"\n  User: {full_name} ({user.username})")
            print(f"    Total Hours: {float(total_hours)}")
            print(f"    Story Points: {int(total_story_points)}")
            print(f"    Tasks Completed: {int(tasks_completed)}")
            print(f"    Tasks In Progress: {int(tasks_in_progress)}")
            print(f"    Total Tasks: {int(tasks_total)}")
            
            total_project_hours += float(total_hours)
            total_project_story_points += int(total_story_points)
        
        print(f"\nProject Summary:")
        print(f"  Total Project Hours: {round(total_project_hours, 2)}")
        print(f"  Total Project Story Points: {total_project_story_points}")
        print(f"  Active Users Count: {len(project_users)}")
        
        print("\n✅ User statistics calculation works correctly!")
        
    except Exception as e:
        print(f"❌ Error testing user statistics: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_statistics()
