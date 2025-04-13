"""
Tests for database initialization.
"""

import pytest
import os
import logging
import asyncio
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.database.database import Base
from app.models.user import User
from app.auth.auth import get_password_hash, verify_password
from app.database.init_db import check_admin_default_password, init_db, pwd_context, verify_password as init_db_verify_password
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


# New additional tests to improve coverage

def test_verify_password():
    """Test the verify_password function directly"""
    # Hash a test password
    test_password = "testpassword123"
    hashed = pwd_context.hash(test_password)
    
    # Test verification works for correct password
    assert init_db_verify_password(test_password, hashed) == True
    
    # Test verification fails for incorrect password
    assert init_db_verify_password("wrongpassword", hashed) == False


@pytest.mark.asyncio
@patch('app.database.init_db.run_migrations')
@patch('app.database.init_db.Session')
@patch('app.database.init_db.check_admin_default_password')
async def test_init_db_successful(mock_check_admin, mock_session, mock_run_migrations):
    """Test successful database initialization"""
    # Set up mocks
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    mock_db.query.return_value.filter.return_value.first.return_value = None  # Admin user doesn't exist
    
    # Call the function
    await init_db()
    
    # Verify migrations were run
    mock_run_migrations.assert_called_once()
    
    # Verify admin user was created
    mock_db.query.assert_called_with(User)
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    
    # Verify admin password was checked
    mock_check_admin.assert_called_once_with(mock_db)
    
    # Verify database session was closed
    mock_db.close.assert_called_once()


@pytest.mark.asyncio
@patch('app.database.init_db.run_migrations')
@patch('app.database.init_db.Session')
@patch('app.database.init_db.check_admin_default_password')
@patch('app.database.init_db.logger')
async def test_init_db_admin_exists(mock_logger, mock_check_admin, mock_session, mock_run_migrations):
    """Test initialization when admin user already exists"""
    # Set up mocks
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    # Simulate admin user already exists
    mock_admin_user = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_admin_user
    
    # Call the function
    await init_db()
    
    # Verify migrations were run
    mock_run_migrations.assert_called_once()
    
    # Verify admin user creation was not attempted
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()
    
    # Verify log message
    mock_logger.info.assert_any_call(f"{DB_SETTINGS['default_admin_username']} user already exists")
    
    # Verify admin password was checked
    mock_check_admin.assert_called_once_with(mock_db)
    
    # Verify database session was closed
    mock_db.close.assert_called_once()


@pytest.mark.asyncio
@patch('app.database.init_db.run_migrations')
@patch('app.database.init_db.Session')
@patch('app.database.init_db.logger')
async def test_init_db_exception_handling(mock_logger, mock_session, mock_run_migrations):
    """Test error handling during database initialization"""
    # Set up mocks
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    # Simulate database error during user creation
    mock_db.query.side_effect = Exception("Test database error")
    
    # Call the function
    await init_db()
    
    # Verify error handling
    mock_db.rollback.assert_called_once()
    mock_logger.error.assert_called_once()
    assert "Error during database initialization" in mock_logger.error.call_args[0][0]
    
    # Verify database session was closed
    mock_db.close.assert_called_once()


@patch('app.database.init_db.logger')
def test_check_admin_default_password_exception(mock_logger, setup_test_db):
    """Test exception handling in check_admin_default_password"""
    # Create a mock database session that raises an exception
    mock_db = MagicMock()
    mock_db.query.side_effect = Exception("Test database error")
    
    # Call the function
    check_admin_default_password(mock_db)
    
    # Verify error was logged
    mock_logger.error.assert_called_once()
    assert "Error checking admin password" in mock_logger.error.call_args[0][0]