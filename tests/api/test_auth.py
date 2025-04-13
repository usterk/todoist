"""
Tests for authentication endpoints.
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.user import User

# Remove test database file if it exists to start with a clean slate
test_db_file = "./test_auth.db"
if os.path.exists(test_db_file):
    os.remove(test_db_file)

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{test_db_file}"
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Create tables before any tests run
Base.metadata.create_all(bind=test_engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Test database session dependency"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override database dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_test_db():
    """Set up test database for each test"""
    # Ensure database is empty before tests
    with TestingSessionLocal() as session:
        # Clear any existing data
        try:
            session.execute(text("DELETE FROM users"))
            session.commit()
        except Exception:
            session.rollback()
    
    yield
    
    # Clean up after tests
    with TestingSessionLocal() as session:
        try:
            session.execute(text("DELETE FROM users"))
            session.commit()
        except Exception:
            session.rollback()


def test_register_user(setup_test_db):
    """Test user registration endpoint"""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "TestPassword123"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email(setup_test_db):
    """Test registration fails with duplicate email"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"username": "testuser1", "email": "test@example.com", "password": "TestPassword123"}
    )
    
    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser2", "email": "test@example.com", "password": "TestPassword123"}
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_duplicate_username(setup_test_db):
    """Test registration fails with duplicate username"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test1@example.com", "password": "TestPassword123"}
    )
    
    # Try to register with same username
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test2@example.com", "password": "TestPassword123"}
    )
    
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


def test_register_password_too_short(setup_test_db):
    """Test registration fails with password that's too short"""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "Short1"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("password" in item["loc"] and "at least" in item["msg"] 
               for item in error_detail)


def test_register_password_no_digits(setup_test_db):
    """Test registration fails with password without digits"""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "NoDigitsHere"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("password" in item["loc"] and "digit" in item["msg"] 
               for item in error_detail)


def test_register_password_no_uppercase(setup_test_db):
    """Test registration fails with password without uppercase letters"""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "nouppercase123"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("password" in item["loc"] and "uppercase" in item["msg"] 
               for item in error_detail)


def test_register_password_no_lowercase(setup_test_db):
    """Test registration fails with password without lowercase letters"""
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "NOLOWERCASE123"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("password" in item["loc"] and "lowercase" in item["msg"] 
               for item in error_detail)


def test_login_success(setup_test_db):
    """Test successful login and token generation"""
    # Register a user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "TestPassword123"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "TestPassword123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(setup_test_db):
    """Test login fails with invalid credentials"""
    # Register a user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "TestPassword123"}
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

# New test cases to increase coverage

def test_register_database_error(setup_test_db, monkeypatch):
    """Test handling of database error during registration"""
    # Create a mock session that raises an exception during commit
    class MockSession:
        def __init__(self):
            pass
            
        def add(self, obj):
            pass
            
        def commit(self):
            raise Exception("Database error")
            
        def rollback(self):
            pass
            
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    return self
                    
                def first(self):
                    return None
            return MockQuery()
            
        def execute(self, *args, **kwargs):
            class MockResult:
                def first(self):
                    return None
            return MockResult()
    
    # Replace the database session with the mock
    def mock_get_db():
        try:
            yield MockSession()
        finally:
            pass
    
    # Store the original override
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Apply the monkey patch
        app.dependency_overrides[get_db] = mock_get_db
        
        # Attempt to register a user
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "email": "test@example.com", "password": "TestPassword123"}
        )
        
        # Check the response
        assert response.status_code == 500
        assert "Failed to create user" in response.json()["detail"]
    finally:
        # Reset the dependency override
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]

def test_login_user_not_found(setup_test_db):
    """Test login with non-existent user email"""
    # Create mock session that simulates non-existent user
    class MockSession:
        def __init__(self):
            pass
            
        def query(self, model):
            class MockQuery:
                def filter(self, condition):
                    return self
                    
                def first(self):
                    return None  # Symulujemy brak użytkownika
            return MockQuery()
        
        def execute(self, *args, **kwargs):
            class MockResult:
                def first(self):
                    return None
            return MockResult()
    
    # Replace the database session with the mock
    def mock_get_db():
        try:
            yield MockSession()
        finally:
            pass
    
    # Store the original override
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Apply the mock
        app.dependency_overrides[get_db] = mock_get_db
        
        # Try to login with non-existent email
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "TestPassword123"}
        )
        
        # Check the response
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    finally:
        # Reset the dependency override
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]

def test_register_malformed_request(setup_test_db):
    """Test registration with malformed request (missing required fields)"""
    # Missing email
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "password": "TestPassword123"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("email" in item["loc"] for item in error_detail)
    
    # Missing username
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "TestPassword123"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("username" in item["loc"] for item in error_detail)
    
    # Missing password
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("password" in item["loc"] for item in error_detail)

def test_login_malformed_request(setup_test_db):
    """Test login with malformed request (missing required fields)"""
    # Missing email
    response = client.post(
        "/api/auth/login",
        json={"password": "TestPassword123"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("email" in item["loc"] for item in error_detail)
    
    # Missing password
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com"}
    )
    
    assert response.status_code == 422
    error_detail = response.json()["detail"]
    assert any("password" in item["loc"] for item in error_detail)