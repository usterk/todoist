"""
User schemas for request and response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class UserBase(BaseModel):
    """Base user schema with common attributes."""
    username: str = Field(..., min_length=3, max_length=50, example="johndoe")
    email: EmailStr = Field(..., example="john@example.com")


class UserCreate(UserBase):
    """Schema for user creation with password."""
    password: str = Field(..., min_length=8, example="SecurePassword123")
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


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


class UserUpdate(BaseModel):
    """Schema for user update data."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="johndoe_updated")
    email: Optional[EmailStr] = Field(None, example="john_updated@example.com")
    password: Optional[str] = Field(None, min_length=8, example="NewSecurePassword123")
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength if provided."""
        if v is None:
            return v
            
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    class Config:
        """Pydantic configuration."""
        orm_mode = True


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[int] = None


class ApiKeyCreate(BaseModel):
    """Schema for API key creation."""
    description: Optional[str] = None


class ApiKeyResponse(BaseModel):
    """Schema for API key response."""
    id: int
    key_value: str
    description: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True