"""
User-related models.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.database import Base


class User(Base):
    """User model for authentication and user management."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with API keys
    api_keys = relationship("ApiKey", back_populates="user")
    
    # Relationship with projects
    projects = relationship("Project", back_populates="owner")


class ApiKey(Base):
    """API Key model for alternative authentication."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_value = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    
    # Relationship with user
    user = relationship("User", back_populates="api_keys")