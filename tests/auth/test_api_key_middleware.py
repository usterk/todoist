import pytest
from unittest import mock
from fastapi import Request, HTTPException

from app.models.user import User, ApiKey
from app.database.database import get_db  # Fixed import path
from app.api.dependencies import get_current_user_from_api_key
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return mock.MagicMock(spec=Session)


@pytest.fixture
def test_user():
    """Create a test user."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        created_at=datetime.utcnow()
    )


@pytest.fixture
def valid_api_key(test_user):
    """Create a valid API key."""
    return ApiKey(
        id=1,
        user_id=test_user.id,
        key_value="test-api-key-123",
        description="Test API Key",
        last_used=None,
        created_at="2023-11-28T12:34:56.789012",
        revoked=False
    )


@pytest.fixture
def revoked_api_key(test_user):
    """Create a revoked API key."""
    return ApiKey(
        id=2,
        user_id=test_user.id,
        key_value="revoked-api-key",
        description="Revoked API Key",
        last_used=None,
        created_at="2023-11-28T12:34:56.789012",
        revoked=True
    )


@pytest.fixture
def mock_request():
    """Create a mock request."""
    return mock.MagicMock(spec=Request)


def test_get_current_user_from_api_key_valid(mock_db, mock_request, test_user, valid_api_key):
    """Test successful API key authentication."""
    # Setup
    mock_request.headers = {"x-api-key": valid_api_key.key_value}
    mock_db.query.return_value.filter.return_value.first.return_value = valid_api_key
    mock_db.query.return_value.get.return_value = test_user
    
    # Execute
    result = get_current_user_from_api_key(mock_request, mock_db)
    
    # Assert
    assert result.id == test_user.id
    assert result.username == test_user.username
    assert result.email == test_user.email
    
    # Verify the key's last_used was updated
    mock_db.commit.assert_called_once()


def test_get_current_user_from_api_key_missing(mock_db, mock_request):
    """Test API key authentication fails when API key is missing."""
    # Setup
    mock_request.headers = {}  # No API key in headers
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_from_api_key(mock_request, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "API key not found" in str(exc_info.value.detail)


def test_get_current_user_from_api_key_invalid(mock_db, mock_request):
    """Test API key authentication fails when API key doesn't exist."""
    # Setup
    mock_request.headers = {"x-api-key": "invalid_key_12345"}
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_from_api_key(mock_request, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value.detail)


def test_get_current_user_from_api_key_revoked(mock_db, mock_request, revoked_api_key):
    """Test API key authentication fails when API key is revoked."""
    # Setup
    mock_request.headers = {"x-api-key": revoked_api_key.key_value}
    mock_db.query.return_value.filter.return_value.first.return_value = revoked_api_key
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_from_api_key(mock_request, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "API key has been revoked" in str(exc_info.value.detail)


def test_get_current_user_from_api_key_user_not_found(mock_db, mock_request, valid_api_key):
    """Test API key authentication fails when user doesn't exist."""
    # Setup
    mock_request.headers = {"x-api-key": valid_api_key.key_value}
    mock_db.query.return_value.filter.return_value.first.return_value = valid_api_key
    mock_db.query.return_value.get.return_value = None  # User not found
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        get_current_user_from_api_key(mock_request, mock_db)
    
    assert exc_info.value.status_code == 401
    assert "User not found" in str(exc_info.value.detail)
