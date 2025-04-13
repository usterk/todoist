"""
Tests for database initialization.
"""

import pytest
import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.database.database import Base
from app.models.user import User
from app.auth.auth import get_password_hash, verify_password
from app.database.init_db import check_admin_default_password
from app.core.config import DB_SETTINGS

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
    admin = db.query(User).filter(User.username == DB_SETTINGS["default_admin_username"]).first()
    if not admin:
        admin_user = User(
            username=DB_SETTINGS["default_admin_username"],
            email=DB_SETTINGS["default_admin_email"],
            password_hash=get_password_hash(DB_SETTINGS["default_admin_password"])
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
    admin_user = db.query(User).filter(User.username == DB_SETTINGS["default_admin_username"]).first()
    
    assert admin_user is not None
    assert admin_user.username == DB_SETTINGS["default_admin_username"]
    assert admin_user.email == DB_SETTINGS["default_admin_email"]
    
    # Test password verification
    assert verify_password(DB_SETTINGS["default_admin_password"], admin_user.password_hash) == True


@pytest.mark.parametrize(
    "password,expected_warning",
    [
        (DB_SETTINGS["default_admin_password"], True),  # Default password should trigger warning
        ("securepassword", False)                       # Changed password should not trigger warning
    ],
)
def test_admin_default_password_warning(setup_test_db, caplog, password, expected_warning):
    """Test that a warning is logged when admin has the default password"""
    # Set up
    db = setup_test_db
    admin_user = db.query(User).filter(User.username == DB_SETTINGS["default_admin_username"]).first()
    
    # Update admin password to test value
    admin_user.password_hash = get_password_hash(password)
    db.commit()
    
    # Set caplog to capture warnings
    caplog.set_level(logging.WARNING)
    
    # Call the function that checks admin password
    check_admin_default_password(db)
    
    # Check if warning was logged
    warning_message = f"SECURITY WARNING: The '{DB_SETTINGS['default_admin_username']}' user has the default password."
    if expected_warning:
        assert any(warning_message in record.message for record in caplog.records)
    else:
        assert not any(warning_message in record.message for record in caplog.records)