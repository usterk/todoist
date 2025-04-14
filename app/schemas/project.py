from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Schema for project creation
class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Project description", max_length=500)

# Schema for project update
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Project name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Project description", max_length=500)

# Schema for project response
class Project(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
