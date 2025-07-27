#!/usr/bin/env python3
"""
Test script to verify the database hierarchy after fixing the relationships
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models.project import Project
from app.models.phase import Phase  
from app.models.milestone import Milestone
from app.models.sprint import Sprint
from app.models.task import Task

def test_hierarchy():
    """Test the database hierarchy relationships"""
    
    # Create database session
    engine = create_engine('sqlite:///ginga_tek.db')
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("🔍 Testing Database Hierarchy...")
        print("=" * 50)
        
        # Test Project level
        projects = db.query(Project).all()
        print(f"📁 Total Projects: {len(projects)}")
        
        if not projects:
            print("❌ No projects found!")
            return
            
        project = projects[0]
        print(f"   Project: {project.name} (ID: {project.id})")
        
        # Test Phase level  
        phases = db.query(Phase).filter(Phase.project_id == project.id).all()
        print(f"📋 Phases in project: {len(phases)}")
        for phase in phases:
            print(f"   - {phase.name} (ID: {phase.id})")
            
        # Test Milestone level
        milestones = db.query(Milestone).filter(Milestone.project_id == project.id).all()
        print(f"🎯 Milestones in project: {len(milestones)}")
        for milestone in milestones:
            # Count sprints for this milestone
            sprint_count = db.query(func.count(Sprint.id)).filter(Sprint.milestone_id == milestone.id).scalar() or 0
            print(f"   - {milestone.name} (ID: {milestone.id}) → {sprint_count} sprints")
            
        # Test Sprint level
        sprints = db.query(Sprint).filter(Sprint.project_id == project.id).all()
        print(f"🏃 Sprints in project: {len(sprints)}")
        for sprint in sprints:
            # Count tasks for this sprint
            task_count = db.query(func.count(Task.id)).filter(Task.sprint_id == sprint.id).scalar() or 0
            print(f"   - {sprint.name} (ID: {sprint.id}) → Milestone: {sprint.milestone_id} → {task_count} tasks")
            
        # Test Task level
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        print(f"📝 Tasks in project: {len(tasks)}")
        for task in tasks:
            sprint_name = "None"
            if task.sprint:
                sprint_name = task.sprint.name
            print(f"   - {task.title} (ID: {task.id}) → Sprint: {sprint_name}")
            
        print("\n✅ Hierarchy Test Complete!")
        print("🔗 Correct Hierarchy: Project → Phase → Milestone → Sprint → Task")
        
    except Exception as e:
        print(f"❌ Error during hierarchy test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()

if __name__ == "__main__":
    test_hierarchy()
