"""
User schemas for request and response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str = Field(..., example="johndoe")
    email: EmailStr = Field(..., example="john@example.com")


class UserCreate(UserBase):
    """Schema for user creation with password."""
    password: str = Field(..., min_length=6, example="SecurePassword123")


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., example="john@example.com")
    password: str = Field(..., example="SecurePassword123")


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    created_at: datetime

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None