import pytest
from unittest import mock
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.user import User, ApiKey
from app.schemas.user import ApiKeyCreate, ApiKeyResponse
from app.api.auth import create_api_key
from app.auth.auth import create_access_token

def test_api_key_model():
    """Test that the ApiKey model has the expected attributes."""
    api_key = ApiKey(
        id=1,
        user_id=2,
        key_value="test_key_123",
        description="Test API Key",
        last_used=None,
        created_at="2023-11-28T12:34:56.789012",
        revoked=False
    )
    
    assert api_key.id == 1
    assert api_key.user_id == 2
    assert api_key.key_value == "test_key_123"
    assert api_key.description == "Test API Key"
    assert api_key.revoked is False

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
        password_hash="hashed_password"
    )

@pytest.fixture
def test_token(test_user):
    """Create a test JWT token."""
    return create_access_token({"sub": str(test_user.id)})

@pytest.mark.asyncio
async def test_generate_api_key_success(mock_db, test_user):
    """Test successful API key generation."""
    # Set up mock
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    api_key_create = ApiKeyCreate(description="Test API Key")
    
    # Przygotowanie mocka dla bazy danych
    def add_mock(api_key):
        api_key.id = 1  # Symulujemy przypisanie ID przez bazę danych
    
    mock_db.add.side_effect = add_mock
    
    # Przygotowanie mocka dla refresh
    def refresh_mock(api_key):
        pass  # Nic nie robimy, ale zapewniamy, że metoda istnieje
    
    mock_db.refresh = refresh_mock
    
    # Call the async function with await
    result = await create_api_key(api_key_create, mock_db, test_user)
    
    # Check the result
    assert isinstance(result, ApiKeyResponse)
    assert result.id == 1
    assert result.description == "Test API Key"
    assert isinstance(result.created_at, datetime)

@pytest.mark.asyncio
async def test_generate_api_key_user_not_found(mock_db):
    """Test API key generation fails when user doesn't exist."""
    # Set up mock
    mock_db.query.return_value.filter.return_value.first.return_value = None
    api_key_create = ApiKeyCreate(description="Test API Key")
    
    with pytest.raises(HTTPException) as exc_info:
        # Call the async function with await
        await create_api_key(api_key_create, mock_db, 999)
    
    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_generate_api_key_no_description(mock_db, test_user):
    """Test API key generation with no description provided."""
    # Set up mock
    mock_db.query.return_value.filter.return_value.first.return_value = test_user
    api_key_create = None
    
    # Przygotowanie mocka dla bazy danych
    def add_mock(api_key):
        api_key.id = 1  # Symulujemy przypisanie ID przez bazę danych
    
    mock_db.add.side_effect = add_mock
    
    # Przygotowanie mocka dla refresh
    def refresh_mock(api_key):
        pass  # Nic nie robimy, ale zapewniamy, że metoda istnieje
    
    mock_db.refresh = refresh_mock
    
    # Call the async function with await
    result = await create_api_key(api_key_create, mock_db, test_user)
    
    # Check the result
    assert isinstance(result, ApiKeyResponse)
    assert result.id == 1
    assert result.description is None
    assert isinstance(result.created_at, datetime)
