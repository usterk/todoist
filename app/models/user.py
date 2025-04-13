from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database.database import Base

class User(Base):
    """
    User model for authentication and task assignment.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        """String representation of user"""
        return f"<User {self.username}>"