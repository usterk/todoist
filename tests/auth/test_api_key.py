import pytest
from unittest import mock
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.api.auth import generate_api_key
from app.schemas.user import ApiKeyCreate
from app.models.user import ApiKey, User
from app.core.security import create_access_token


def test_api_key_model():
    """Test that the ApiKey model has the expected attributes."""
    api_key = ApiKey()
    assert hasattr(api_key, 'id')
    assert hasattr(api_key, 'user_id')
    assert hasattr(api_key, 'key_value')
    assert hasattr(api_key, 'description')
    assert hasattr(api_key, 'last_used')
    assert hasattr(api_key, 'created_at')
    assert hasattr(api_key, 'revoked')


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
def test_token(test_user):
    """Create a test JWT token."""
    return create_access_token({"sub": str(test_user.id)})


def test_generate_api_key_success(mock_db, test_user):
    """Test successful API key generation."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    api_key_create = ApiKeyCreate(description="Test API Key")
    
    # Execute
    result = generate_api_key(mock_db, test_user.id, api_key_create)
    
    # Assert
    assert result.key_value is not None
    assert len(result.key_value) >= 32  # API key should be at least 32 chars long
    assert result.description == "Test API Key"
    assert not result.revoked
    
    # Verify DB interaction
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_generate_api_key_user_not_found(mock_db):
    """Test API key generation fails when user doesn't exist."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None
    api_key_create = ApiKeyCreate(description="Test API Key")
    
    # Execute and Assert
    with pytest.raises(HTTPException) as exc_info:
        generate_api_key(mock_db, 999, api_key_create)
    
    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_called()


def test_generate_api_key_no_description(mock_db, test_user):
    """Test API key generation with no description provided."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    api_key_create = ApiKeyCreate()  # No description
    
    # Execute
    result = generate_api_key(mock_db, test_user.id, api_key_create)
    
    # Assert
    assert result.description is None
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
