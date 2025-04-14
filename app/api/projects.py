from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models.user import User
from ..schemas.project import Project, ProjectCreate, ProjectUpdate
from ..models.project import Project as ProjectModel
from ..api.dependencies import get_current_user

# Create router
router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={401: {"description": "Authentication required"}},
)

@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project.
    
    - **name**: Required. The name of the project
    - **description**: Optional. Details about the project
    """
    db_project = ProjectModel(
        name=project.name,
        description=project.description,
        user_id=current_user.id  # Dodanie powiązania z użytkownikiem
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.get("", response_model=List[Project])
async def get_projects(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=100, description="Max number of items to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all projects with pagination.
    
    - **skip**: Number of projects to skip (for pagination)
    - **limit**: Maximum number of projects to return (for pagination)
    """
    # Filtrowanie projektów dla zalogowanego użytkownika
    projects = db.query(ProjectModel).filter(
        ProjectModel.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=Project)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single project by ID.
    
    - **project_id**: The ID of the project to retrieve
    """
    # Dodanie filtrowania po użytkowniku dla bezpieczeństwa
    project = db.query(ProjectModel).filter(
        ProjectModel.id == project_id,
        ProjectModel.user_id == current_user.id
    ).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a project.
    
    - **project_id**: The ID of the project to update
    - **name**: Optional. New name for the project
    - **description**: Optional. New description for the project
    """
    # Dodanie filtrowania po użytkowniku dla bezpieczeństwa
    db_project = db.query(ProjectModel).filter(
        ProjectModel.id == project_id,
        ProjectModel.user_id == current_user.id
    ).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields if provided
    if project_update.name is not None:
        db_project.name = project_update.name
    if project_update.description is not None:
        db_project.description = project_update.description
    
    db.commit()
    db.refresh(db_project)
    
    return db_project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project.
    
    - **project_id**: The ID of the project to delete
    """
    # Dodanie filtrowania po użytkowniku dla bezpieczeństwa
    db_project = db.query(ProjectModel).filter(
        ProjectModel.id == project_id,
        ProjectModel.user_id == current_user.id
    ).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    
    return None
