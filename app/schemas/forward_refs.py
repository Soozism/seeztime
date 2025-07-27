"""
Forward reference resolution for schemas
This file helps resolve circular import issues between schemas
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserSimple
    from app.schemas.project import ProjectSimple
    from app.schemas.sprint import SprintSimple

# This will be imported after all models are defined
def resolve_forward_refs():
    """Resolve forward references in all schemas"""
    from app.schemas.task import TaskResponseExpanded
    from app.schemas.project import ProjectResponseExpanded
    from app.schemas.sprint import SprintResponseExpanded
    from app.schemas.user import UserSimple
    from app.schemas.project import ProjectSimple
    from app.schemas.sprint import SprintSimple
    
    # Resolve forward references
    TaskResponseExpanded.model_rebuild()
    ProjectResponseExpanded.model_rebuild()
    SprintResponseExpanded.model_rebuild()
