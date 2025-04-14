"""
Tests for the auth.py module, focusing on authentication utilities.
"""

import pytest
import os
from datetime import datetime, timedelta
import asyncio
from typing import Optional
from fastapi import FastAPI, Depends, Header, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from jose import jwt, JWTError

from app.auth.auth import (
    verify_password,
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_user_from_token,
    get_current_user_from_api_key,
    get_current_user_from_jwt,
    SECRET_KEY,
    ALGORITHM,
)
from app.database.database import get_db

# Test database setup
test_db_file = "./test_auth.db"
if os.path.exists(test_db_file):
    os.remove(test_db_file)

SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{test_db_file}"
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Create base model for test
Base = declarative_base()

# Define test model
class User(Base):
    """Test User model for authentication tests"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    api_keys = relationship("ApiKey", back_populates="user")

class ApiKey(Base):
    """Test API Key model"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    key_value = Column(String, unique=True)
    description = Column(String, nullable=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="api_keys")

# Create tables
Base.metadata.create_all(bind=test_engine)

# Create test database session
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Test app
test_app = FastAPI()

# Override database dependency
def override_get_db():
    """Test database session dependency"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

# Test endpoints
@test_app.get("/protected")
async def protected_route(current_user = Depends(get_current_user)):
    return {"user_id": current_user.id}

@test_app.get("/token-only")
async def token_route(current_user = Depends(get_current_user_from_token)):
    return {"user_id": current_user.id}

@test_app.get("/apikey-only")
async def apikey_route(current_user = Depends(get_current_user_from_api_key)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required")
    return {"user_id": current_user.id}

# Apply dependency override
test_app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(test_app)

@pytest.fixture
def test_db():
    """Fixture for database session"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(test_db):
    """Fixture to create a test user"""
    # Clean up existing data
    test_db.execute(text("DELETE FROM api_keys"))
    test_db.execute(text("DELETE FROM users"))
    test_db.commit()
    
    # Create test user with properly hashed password
    hashed_password = get_password_hash("testpassword")
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hashed_password
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    
    # Create an API key for the user
    api_key = ApiKey(
        user_id=user.id,
        key_value="test-api-key-123",
        description="Test API key"
    )
    test_db.add(api_key)
    
    # Create a revoked API key
    revoked_key = ApiKey(
        user_id=user.id,
        key_value="revoked-key-456",
        description="Revoked key",
        revoked=True
    )
    test_db.add(revoked_key)
    test_db.commit()
    
    yield user
    
    # Clean up
    test_db.execute(text("DELETE FROM api_keys"))
    test_db.execute(text("DELETE FROM users"))
    test_db.commit()

# Tests for auth functions
def test_password_hashing():
    """Test password hashing and verification"""
    password = "secretpassword123"
    hashed = get_password_hash(password)
    
    # Verify that hashed password is not the original password
    assert hashed != password
    
    # Verify that we can validate the password against its hash
    assert verify_password(password, hashed)
    
    # Verify that incorrect password fails validation
    assert not verify_password("wrongpassword", hashed)

def test_authenticate_user(test_user, test_db):
    """Test user authentication with correct and incorrect credentials"""
    # Test successful authentication
    user = authenticate_user(test_db, "test@example.com", "testpassword")
    assert user is not False
    assert user.email == "test@example.com"
    
    # Test failed authentication - wrong password
    user = authenticate_user(test_db, "test@example.com", "wrongpassword")
    assert user is False
    
    # Test failed authentication - user not found
    user = authenticate_user(test_db, "nonexistent@example.com", "testpassword")
    assert user is False

def test_create_access_token():
    """Test creation of JWT access tokens"""
    # Test with explicit user_id parameter
    token1 = create_access_token(user_id=123)
    assert token1 is not None
    assert isinstance(token1, str)
    
    # Decode the token and verify claims
    payload = jwt.decode(token1, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "123"
    assert "exp" in payload
    
    # Test with custom data
    custom_data = {"role": "admin", "user_id": 456}
    token2 = create_access_token(data=custom_data)
    payload = jwt.decode(token2, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["role"] == "admin"
    assert payload["user_id"] == 456
    assert "exp" in payload
    
    # Test with custom expiry
    expiry = timedelta(minutes=60)
    token3 = create_access_token(user_id=789, expires_delta=expiry)
    payload = jwt.decode(token3, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "789"

@pytest.mark.asyncio
async def test_get_current_user_from_token_invalid_format():
    """Test get_current_user_from_token with invalid token format"""
    # Ustawiamy token z niepoprawną wartością sub
    invalid_token = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30), "sub": "not_a_number"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    # Mock bazy danych
    db_mock = None
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_from_token(token=invalid_token, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_from_token_missing_sub():
    """Test get_current_user_from_token with token missing sub claim"""
    # Token bez pola sub
    token_no_sub = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    # Mock bazy danych
    db_mock = None
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_from_token(token=token_no_sub, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_from_token_invalid_user():
    """Test get_current_user_from_token with valid token but nonexistent user"""
    # Token dla nieistniejącego użytkownika
    token_invalid_user = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30), "sub": "99999"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    # Mock dla sesji bazy danych
    class MockDB:
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    return self
                
                def first(self):
                    return None  # Użytkownik nie istnieje
            return MockQuery()
    
    db_mock = MockDB()
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_from_token(token=token_invalid_user, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_no_authentication():
    """Test get_current_user with no authentication provided"""
    # Brak tokena JWT i klucza API
    request_mock = None
    token = None
    x_api_key = None
    db_mock = None
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request=request_mock, token=token, x_api_key=x_api_key, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Not authenticated" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_from_api_key_success():
    """Test successful API key authentication"""
    # Valid API key
    x_api_key = "test-api-key-123"
    
    # Mock for database session
    class MockDB:
        def execute(self, statement, params=None):
            class MockResult:
                def first(self):
                    # Return user_id from the ApiKey table
                    return [1]
            return MockResult()
            
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    return self
                
                def first(self):
                    # Return a mock user
                    user = User(
                        id=1,
                        username="testuser",
                        email="test@example.com",
                        password_hash="hashed_password"
                    )
                    return user
            return MockQuery()
        
        def commit(self):
            pass
    
    db_mock = MockDB()
    
    # Call the function
    user = await get_current_user_from_api_key(x_api_key=x_api_key, db=db_mock)
    
    # Verify returned user
    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"

@pytest.mark.asyncio
async def test_get_current_user_from_api_key_no_key():
    """Test API key authentication with no key provided"""
    # No API key
    x_api_key = None
    db_mock = None
    
    # Call the function
    user = await get_current_user_from_api_key(x_api_key=x_api_key, db=db_mock)
    
    # Should return None, not raise an exception
    assert user is None

@pytest.mark.asyncio
async def test_get_current_user_from_api_key_invalid_key():
    """Test API key authentication with invalid key"""
    # Invalid API key
    x_api_key = "invalid-key"
    
    # Mock for database session that returns no result
    class MockDB:
        def execute(self, statement, params=None):
            class MockResult:
                def first(self):
                    # No key found
                    return None
            return MockResult()
    
    db_mock = MockDB()
    
    # Call the function and expect an exception
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_from_api_key(x_api_key=x_api_key, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid API key" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_from_api_key_no_user():
    """Test API key authentication with valid key but missing user"""
    # Valid API key
    x_api_key = "test-api-key-123"
    
    # Mock for database session
    class MockDB:
        def execute(self, statement, params=None):
            class MockResult:
                def first(self):
                    # Return user_id from the ApiKey table
                    return [999]  # ID of non-existent user
            return MockResult()
            
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    return self
                
                def first(self):
                    # No user found
                    return None
            return MockQuery()
        
        def commit(self):
            pass
    
    db_mock = MockDB()
    
    # Call the function and expect an exception
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_from_api_key(x_api_key=x_api_key, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "User associated with API key not found" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_from_api_key_database_error():
    """Test API key authentication with database error"""
    # Valid API key
    x_api_key = "test-api-key-123"
    
    # Mock for database session that raises an exception
    class MockDB:
        def execute(self, statement, params=None):
            raise Exception("Database error")
    
    db_mock = MockDB()
    
    # Call the function and expect an exception
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_from_api_key(x_api_key=x_api_key, db=db_mock)
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error processing API key" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_user_jwt_priority():
    """Test that JWT takes priority over API key in get_current_user"""
    # Both JWT and API key provided
    token = jwt.encode(
        {"exp": datetime.utcnow() + timedelta(minutes=30), "sub": "1"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    x_api_key = "test-api-key-123"
    
    # Mock for request
    request_mock = None
    
    # Mock for database session
    class MockDB:
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    return self
                
                def first(self):
                    # Return user for JWT token (ID=1)
                    user = User(
                        id=1,
                        username="jwt_user",
                        email="jwt@example.com",
                        password_hash="hashed_password"
                    )
                    return user
            return MockQuery()
    
    db_mock = MockDB()
    
    # Call the function
    user = await get_current_user(
        request=request_mock,
        token=token,
        x_api_key=x_api_key,
        db=db_mock
    )
    
    # Should use JWT token and return the JWT user
    assert user is not None
    assert user.username == "jwt_user"

@pytest.mark.asyncio
async def test_get_current_user_jwt_failure_apikey_fallback():
    """Test that API key is used as fallback if JWT validation fails"""
    # Invalid JWT token but valid API key
    token = "invalid_token"
    x_api_key = "test-api-key-123"
    
    # Mock for request
    request_mock = None
    
    # Mock for database session
    class MockDB:
        def execute(self, statement, params=None):
            class MockResult:
                def first(self):
                    # Return user_id from the ApiKey table
                    return [2]
            return MockResult()
            
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    # Check if we're querying for the API key user
                    if "id" in str(condition) and "2" in str(condition):
                        return self
                    # For any other query (JWT), return a different self that will return None
                    return MockQuery()
                
                def first(self):
                    # Return user for API key (ID=2)
                    user = User(
                        id=2,
                        username="apikey_user",
                        email="apikey@example.com",
                        password_hash="hashed_password"
                    )
                    return user
            return MockQuery()
            
        def commit(self):
            pass
    
    db_mock = MockDB()
    
    # Call the function
    user = await get_current_user(
        request=request_mock,
        token=token,
        x_api_key=x_api_key,
        db=db_mock
    )
    
    # Should fall back to API key and return the API key user
    assert user is not None
    assert user.username == "apikey_user"

@pytest.mark.asyncio
async def test_get_current_user_token_error():
    """Test error handling in get_current_user when token is invalid"""
    # Invalid token format
    token = "invalid_token"
    x_api_key = None
    request_mock = None
    db_mock = None
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            request=request_mock,
            token=token,
            x_api_key=x_api_key,
            db=db_mock
        )
    
    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in str(exc_info.value.detail)