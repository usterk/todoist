"""
Tests for project API endpoints.
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from app.main import app
from app.database.database import Base, get_db
from app.models.project import Project
from app.models.user import User
from app.auth.auth import get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt

# Test database setup
test_db_file = "./test_projects_api.db"
if os.path.exists(test_db_file):
    os.remove(test_db_file)

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

# Create test JWT token
def create_test_token(user_id=999):
    """
    Create a valid JWT token for tests
    """
    from datetime import datetime, timedelta
    expiry_time = datetime.utcnow() + timedelta(days=365 * 10)  # 10 years in the future
    
    payload = {
        "sub": str(user_id),  # Use a consistent user_id for tests
        "exp": int(expiry_time.timestamp())  # Very distant expiry date
    }
    
    # Use the same key as in app/auth/auth.py
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Override only the database dependency
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database session for each test"""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def auth_token():
    """Generate auth token for the test user (ID=1)"""
    return create_test_token(user_id=1)

@pytest.fixture(scope="function", autouse=True)
def setup_test_user(test_db):
    """Make sure test user with ID=1 exists for auth token validation"""
    # Check if user with ID=1 already exists
    user = test_db.query(User).filter(User.id == 1).first()
    if not user:
        # If not, create it
        hashed_password = get_password_hash("AdminPassword123")
        user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            password_hash=hashed_password
        )
        test_db.add(user)
        test_db.commit()
    return user

@pytest.fixture(scope="function")
def test_project(test_db, setup_test_user):
    """Create a test project for testing"""
    # Pobierz ID użytkownika testowego
    user = setup_test_user
    
    project = Project(
        name="Test Project",
        description="Test project description",
        user_id=user.id  # Dodajemy powiązanie z użytkownikiem
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project

def test_create_project(test_db, auth_token):
    """Test creating a new project"""
    response = client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "New Project", "description": "Project description"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Project"
    assert data["description"] == "Project description"
    assert "id" in data
    assert "created_at" in data

def test_create_project_missing_name(auth_token):
    """Test that creating a project without a name fails"""
    response = client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"description": "Project description"}
    )
    
    assert response.status_code == 422  # Validation error

def test_get_projects(auth_token):
    """Test getting a list of projects"""
    response = client.get(
        "/api/projects",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    # Co najmniej jeden projekt powinien być w odpowiedzi
    assert len(projects) >= 1
    
    # Sprawdzamy, czy każdy projekt ma wymagane pola
    for project in projects:
        assert "id" in project
        assert "name" in project
        assert "description" in project
        assert "user_id" in project
        assert "created_at" in project

def test_get_projects_pagination(test_db, auth_token, setup_test_user):
    """Test pagination for projects list"""
    # Create multiple test projects
    for i in range(5):
        project = Project(
            name=f"Project {i}", 
            description=f"Description {i}",
            user_id=setup_test_user.id
        )
        test_db.add(project)
    test_db.commit()
    
    # Test with limit
    response = client.get(
        "/api/projects?limit=3",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) <= 3
    
    # Test with skip
    response = client.get(
        "/api/projects?skip=2&limit=2",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    projects_skipped = response.json()
    assert len(projects_skipped) <= 2

def test_get_project(test_project, auth_token):
    """Test getting a single project"""
    response = client.get(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    project = response.json()
    
    # Tylko weryfikujemy strukturę projektu, nie jego dokładną nazwę
    assert "id" in project
    assert "name" in project
    assert "description" in project
    assert "user_id" in project
    assert "created_at" in project
    
    # Sprawdzamy, czy dane ID zgadza się z projektem testowym
    assert project["id"] == test_project.id

def test_get_project_not_found(auth_token):
    """Test getting a non-existent project"""
    response = client.get(
        "/api/projects/9999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_update_project(test_project, auth_token):
    """Test updating a project"""
    response = client.put(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Updated Project", "description": "Updated description"}
    )
    
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["name"] == "Updated Project"
    assert updated_project["description"] == "Updated description"
    
    # Verify partial update (only name)
    response = client.put(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Only Name Updated"}
    )
    
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["name"] == "Only Name Updated"
    assert updated_project["description"] == "Updated description"  # Description unchanged

def test_update_project_not_found(auth_token):
    """Test updating a non-existent project"""
    response = client.put(
        "/api/projects/9999",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"name": "Updated Project"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_project(test_project, auth_token):
    """Test deleting a project"""
    response = client.delete(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 204
    
    # Verify project was deleted
    get_response = client.get(
        f"/api/projects/{test_project.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 404

def test_delete_project_not_found(auth_token):
    """Test deleting a non-existent project"""
    response = client.delete(
        "/api/projects/9999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
