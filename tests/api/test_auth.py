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
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
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
        json={"username": "testuser1", "email": "test@example.com", "password": "testpassword"}
    )
    
    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser2", "email": "test@example.com", "password": "testpassword"}
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_duplicate_username(setup_test_db):
    """Test registration fails with duplicate username"""
    # Register first user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test1@example.com", "password": "testpassword"}
    )
    
    # Try to register with same username
    response = client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test2@example.com", "password": "testpassword"}
    )
    
    assert response.status_code == 400
    assert "Username already taken" in response.json()["detail"]


def test_login_success(setup_test_db):
    """Test successful login and token generation"""
    # Register a user
    client.post(
        "/api/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "testpassword"}
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
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]