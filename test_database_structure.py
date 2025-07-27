"""
Simple test for the new hierarchical structure
"""

import sqlite3
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models import User, Project
from app.models.phase import Phase
from app.models.milestone import Milestone
from app.models.sprint import Sprint

def test_database_structure():
    """Test the new database structure"""
    db = SessionLocal()
    
    try:
        # Get the first project
        project = db.query(Project).first()
        if not project:
            print("No projects found")
            return False
            
        print(f"Testing with project: {project.name} (ID: {project.id})")
        
        # Create a test phase
        phase = Phase(
            name="Test Phase",
            description="Testing the new phase structure",
            estimated_hours=100.0,
            project_id=project.id
        )
        db.add(phase)
        db.commit()
        db.refresh(phase)
        print(f"✅ Phase created: {phase.name} (ID: {phase.id})")
        
        # Create a test milestone
        milestone = Milestone(
            name="Test Milestone",
            description="Testing the new milestone structure",
            estimated_hours=50.0,
            phase_id=phase.id,
            project_id=project.id
        )
        db.add(milestone)
        db.commit()
        db.refresh(milestone)
        print(f"✅ Milestone created: {milestone.name} (ID: {milestone.id})")
        
        # Create a test sprint
        sprint = Sprint(
            name="Test Sprint",
            description="Testing the new sprint structure",
            estimated_hours=25.0,
            milestone_id=milestone.id,
            project_id=project.id
        )
        db.add(sprint)
        db.commit()
        db.refresh(sprint)
        print(f"✅ Sprint created: {sprint.name} (ID: {sprint.id})")
        
        # Test the relationships
        print(f"\n🔗 Testing relationships:")
        print(f"Project '{project.name}' has {len(project.phases)} phases")
        print(f"Phase '{phase.name}' has {len(phase.milestones)} milestones")
        print(f"Milestone '{milestone.name}' has {len(milestone.sprints)} sprints")
        
        # Clean up - remove the test data
        db.delete(sprint)
        db.delete(milestone)
        db.delete(phase)
        db.commit()
        print(f"\n🧹 Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing new hierarchical project structure in database...")
    success = test_database_structure()
    if success:
        print("✅ Database structure test passed!")
    else:
        print("❌ Database structure test failed!")
