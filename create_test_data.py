"""
Create test data for the new hierarchical structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.phase import Phase
from app.models.milestone import Milestone
from app.models.sprint import Sprint
from app.models.enums import UserRole, ProjectStatus, SprintStatus

def create_test_data():
    """Create test data for our hierarchical structure"""
    db = SessionLocal()
    
    try:
        print("Creating test data...")
        
        # Create a test user
        user = User(
            username='admin',
            email='admin@gingatek.com',
            first_name='Admin',
            last_name='User',
            role=UserRole.ADMIN,
            password_hash='hashed_password_here'
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ Created user: {user.username}")
        
        # Create a test project
        project = Project(
            name='E-commerce Platform',
            description='Building a modern e-commerce platform',
            estimated_hours=500.0,
            status=ProjectStatus.ACTIVE,
            created_by_id=user.id
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        print(f"✅ Created project: {project.name}")
        
        # Create phases
        phases_data = [
            ('Planning Phase', 'Initial planning and requirements gathering', 80.0),
            ('Development Phase', 'Core development and implementation', 300.0),
            ('Testing Phase', 'Quality assurance and testing', 80.0),
            ('Deployment Phase', 'Production deployment and launch', 40.0)
        ]
        
        phases = []
        for name, desc, hours in phases_data:
            phase = Phase(
                name=name,
                description=desc,
                estimated_hours=hours,
                project_id=project.id
            )
            db.add(phase)
            db.commit()
            db.refresh(phase)
            phases.append(phase)
            print(f"✅ Created phase: {phase.name}")
        
        # Create milestones for the first phase
        planning_phase = phases[0]
        milestones_data = [
            ('Requirements Complete', 'All requirements documented and approved', 40.0),
            ('Architecture Design', 'System architecture and design completed', 40.0)
        ]
        
        milestones = []
        for name, desc, hours in milestones_data:
            milestone = Milestone(
                name=name,
                description=desc,
                estimated_hours=hours,
                phase_id=planning_phase.id,
                project_id=project.id
            )
            db.add(milestone)
            db.commit()
            db.refresh(milestone)
            milestones.append(milestone)
            print(f"✅ Created milestone: {milestone.name}")
        
        # Create sprints for the first milestone
        req_milestone = milestones[0]
        sprints_data = [
            ('Sprint 1 - User Stories', 'Define user stories and acceptance criteria', 20.0),
            ('Sprint 2 - Technical Specs', 'Technical specifications and wireframes', 20.0)
        ]
        
        for name, desc, hours in sprints_data:
            sprint = Sprint(
                name=name,
                description=desc,
                estimated_hours=hours,
                status=SprintStatus.PLANNED,
                milestone_id=req_milestone.id,
                project_id=project.id
            )
            db.add(sprint)
            db.commit()
            db.refresh(sprint)
            print(f"✅ Created sprint: {sprint.name}")
        
        print(f"\n🎉 Test data created successfully!")
        print(f"   - 1 user: {user.username}")
        print(f"   - 1 project: {project.name}")
        print(f"   - {len(phases)} phases")
        print(f"   - {len(milestones)} milestones")
        print(f"   - {len(sprints_data)} sprints")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = create_test_data()
    if success:
        print("\n✅ Test data creation completed!")
    else:
        print("\n❌ Test data creation failed!")
