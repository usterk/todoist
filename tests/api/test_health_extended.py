"""
Extended tests for health check endpoint to improve test coverage.
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.database.database import Base, get_db
from app.api.health import health_check

# Test database setup
test_db_file = "./test_health_extended.db"
if os.path.exists(test_db_file):
    os.remove(test_db_file)

SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{test_db_file}"
test_engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# Create tables
Base.metadata.create_all(bind=test_engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override database dependency
def override_get_db():
    """Test database session dependency"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply dependency override
app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

def test_health_check_success():
    """Test health check endpoint with successful database connection"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "api_version" in data
    assert data["database"] == "connected"
    # No diagnostics should be included when connection is successful
    assert "database_diagnostics" not in data

def test_health_check_db_query_failure():
    """Test health check endpoint when database query fails"""
    # Create a mock DB session that raises an exception on execute
    class MockDBFailure:
        def execute(self, *args, **kwargs):
            raise SQLAlchemyError("Test database error")
    
    # Override get_db dependency to use our mock
    def mock_get_db():
        yield MockDBFailure()
    
    # Store original override
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Apply our mock
        app.dependency_overrides[get_db] = mock_get_db
        
        # Make the request
        response = client.get("/health")
        
        # Check the response
        assert response.status_code == 200  # Still returns 200 but with error details
        data = response.json()
        assert data["status"] == "ok"  # API itself is still OK
        assert data["database"] == "disconnected"
        assert "database_diagnostics" in data
        assert "error" in data["database_diagnostics"]
        assert "Test database error" in data["database_diagnostics"]["error"]
    finally:
        # Restore original dependency
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]

def test_health_check_db_unexpected_result():
    """Test health check when database returns unexpected result"""
    # Create a mock DB session that returns an unexpected value
    class MockDBUnexpectedResult:
        def execute(self, *args, **kwargs):
            class MockResult:
                def fetchone(self):
                    return [None]  # Not 1 as expected
            return MockResult()
    
    # Override get_db dependency
    def mock_get_db():
        yield MockDBUnexpectedResult()
    
    # Store original override
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Apply our mock
        app.dependency_overrides[get_db] = mock_get_db
        
        # Make the request
        response = client.get("/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "disconnected"
        assert "database_diagnostics" in data
        assert "query_result" in data["database_diagnostics"]
    finally:
        # Restore original dependency
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]

def test_health_check_db_unexpected_error():
    """Test health check when an unexpected error occurs"""
    # Create a mock DB session that raises a generic exception
    class MockDBGenericError:
        def execute(self, *args, **kwargs):
            raise RuntimeError("Unexpected error")
    
    # Override get_db dependency
    def mock_get_db():
        yield MockDBGenericError()
    
    # Store original override
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Apply our mock
        app.dependency_overrides[get_db] = mock_get_db
        
        # Make the request
        response = client.get("/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "disconnected"
        assert "database_diagnostics" in data
        assert "error" in data["database_diagnostics"]
        assert "Unexpected error" in data["database_diagnostics"]["error"]
    finally:
        # Restore original dependency
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]

@patch('os.path.exists')
def test_health_check_db_file_not_exists(mock_exists):
    """Test health check when database file does not exist"""
    # Setup mock to say file doesn't exist
    mock_exists.return_value = False
    
    # Create a mock DB session for a disconnected state
    class MockDBDisconnected:
        def execute(self, *args, **kwargs):
            raise SQLAlchemyError("No such file")
    
    # Override get_db dependency
    def mock_get_db():
        yield MockDBDisconnected()
    
    # Store original override
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Apply our mock
        app.dependency_overrides[get_db] = mock_get_db
        
        # Make the request
        response = client.get("/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "disconnected"
        assert "database_diagnostics" in data
        assert "file_exists" in data["database_diagnostics"]
        assert data["database_diagnostics"]["file_exists"] is False
    finally:
        # Restore original dependency
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]

# Direct test of the health_check function using async/await
@pytest.mark.asyncio
async def test_health_check_function_directly():
    """Test the health_check function directly"""
    # Create a mock DB session
    db_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.fetchone.return_value = [1]
    db_mock.execute.return_value = result_mock
    
    # Call the function directly
    result = await health_check(db=db_mock)
    
    # Check the result
    assert result["status"] == "ok"
    assert "api_version" in result
    assert result["database"] == "connected"
    assert "database_diagnostics" not in result