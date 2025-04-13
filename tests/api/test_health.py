"""
Tests for health check endpoint.
"""

import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

# Remove test database file if it exists to start with a clean slate
test_db_file = "./test.db"
if os.path.exists(test_db_file):
    os.remove(test_db_file)

# Create test database
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
    # Ensure database connection is working
    with TestingSessionLocal() as session:
        try:
            session.execute(text("SELECT 1"))
            session.commit()
        except Exception:
            session.rollback()
    
    yield
    
    # No cleanup needed for this test


def test_health_endpoint(setup_test_db):
    """Test health check endpoint returns 200 and database status is connected"""
    # Tworzymy klasę MockSession symulującą udane połączenie z bazą danych
    class MockSessionConnected:
        def __init__(self):
            pass
            
        def execute(self, statement, params=None):
            class MockResult:
                def fetchone(self):
                    return [1]
            return MockResult()
    
    # Funkcja zastępująca oryginalną zależność get_db
    def mock_get_db():
        try:
            yield MockSessionConnected()
        finally:
            pass
    
    # Zapisanie oryginalnej zależności
    original_override = app.dependency_overrides.get(get_db)
    
    try:
        # Zastosowanie mocka
        app.dependency_overrides[get_db] = mock_get_db
        
        # Wywołanie testu
        response = client.get("/health")
        
        # Sprawdzenie odpowiedzi
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["database"] == "connected"
    finally:
        # Przywrócenie oryginalnej zależności
        if original_override:
            app.dependency_overrides[get_db] = original_override
        else:
            del app.dependency_overrides[get_db]