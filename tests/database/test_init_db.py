"""
Tests for database initialization.
"""

import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.database.database import Base
from app.models.user import User
from app.auth.auth import get_password_hash

# Test database connection
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def setup_test_db():
    """Set up a clean test database for each test"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create admin user manually for testing purposes
    db = TestingSessionLocal()
    
    # Check if admin user already exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin")
        )
        db.add(admin_user)
        db.commit()
    
    yield db
    
    # Clean up
    db.close()
    Base.metadata.drop_all(bind=test_engine)


def test_admin_user_creation(setup_test_db):
    """Test that the admin user is created during database initialization"""
    db = setup_test_db
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    assert admin_user is not None
    assert admin_user.username == "admin"
    assert admin_user.email == "admin@example.com"
    
    # Test password verification
    from app.auth.auth import verify_password
    assert verify_password("admin", admin_user.password_hash) == True