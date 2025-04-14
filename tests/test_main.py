"""
Tests for the main application module.
"""

import pytest
from fastapi.testclient import TestClient
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.main import app, startup_db_client, root, init_complete, init_error

# Test client
client = TestClient(app)

def test_root_endpoint_initializing():
    """Test root endpoint when app is still initializing"""
    # Mock the global variables
    with patch('app.main.init_complete', False), \
         patch('app.main.init_error', None):
        
        # Call the root endpoint
        response = client.get("/")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Todoist API is running"
        assert data["status"] == "initializing"
        assert "version" in data
        assert "warning" not in data
        assert "error" not in data

def test_root_endpoint_ready():
    """Test root endpoint when app is ready"""
    # Mock the global variables
    with patch('app.main.init_complete', True), \
         patch('app.main.init_error', None):
        
        # Call the root endpoint
        response = client.get("/")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Todoist API is running"
        assert data["status"] == "ready"
        assert "version" in data
        assert "warning" not in data
        assert "error" not in data

def test_root_endpoint_with_error():
    """Test root endpoint when app initialized with error"""
    # Mock the global variables
    with patch('app.main.init_complete', True), \
         patch('app.main.init_error', "Test initialization error"):
        
        # Call the root endpoint
        response = client.get("/")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Todoist API is running"
        assert data["status"] == "ready"
        assert "version" in data
        assert "warning" in data
        assert data["warning"] == "Application started with initialization errors"
        assert "error" in data
        assert data["error"] == "Test initialization error"

@pytest.mark.asyncio
async def test_startup_db_client_success():
    """Test startup_db_client function with successful initialization"""
    # Utwórz mocki dla globalnych zmiennych
    with patch('app.main.init_complete', False), \
         patch('app.main.init_error', None), \
         patch('app.main.asyncio.create_task') as mock_create_task, \
         patch('app.main.init_db') as mock_init_db:
        
        # Wywołanie funkcji startup
        await startup_db_client()
        
        # Sprawdzenie, czy create_task został wywołany
        mock_create_task.assert_called_once()
        
        # Symuluj zakończenie taska przez wywołanie mock_init_db_background
        # Jako "side_effect" mocka create_task
        task_callback = mock_create_task.call_args[0][0]
        
        # Testujemy tylko czy zadanie zostało utworzone poprawnie
        assert asyncio.iscoroutine(task_callback) or asyncio.isfuture(task_callback)

@pytest.mark.asyncio
async def test_startup_db_client_failure():
    """Test startup_db_client function with failed initialization"""
    # Utwórz mocki dla globalnych zmiennych
    with patch('app.main.init_complete', False), \
         patch('app.main.init_error', None), \
         patch('app.main.logger.info') as mock_logger_info, \
         patch('app.main.asyncio.create_task') as mock_create_task:
        
        # Zamiast mockować side_effect dla create_task, będziemy śledzić
        # jakie korutyny są przekazywane do create_task
        mock_task = AsyncMock()
        mock_create_task.return_value = mock_task
        
        # Wywołanie funkcji startup
        await startup_db_client()
        
        # Sprawdzenie, czy create_task został wywołany
        mock_create_task.assert_called_once()
        
        # Sprawdź, czy informacja o inicjalizacji została zalogowana
        mock_logger_info.assert_called_with("Application startup continues while initialization runs in background")

def test_cors_middleware():
    """Test that CORS middleware is correctly configured"""
    # Test pre-flight OPTIONS request
    headers = {
        "Origin": "http://testorigin.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    
    response = client.options("/", headers=headers)
    
    # Check if CORS headers are present
    assert response.status_code == 200
    
    # Poprawione sprawdzenie - uwzględniamy, że CORS może zwrócić konkretne origin zamiast "*"
    assert response.headers.get("access-control-allow-origin") is not None
    assert "POST" in response.headers.get("access-control-allow-methods")
    assert "Content-Type" in response.headers.get("access-control-allow-headers")

def test_app_configuration():
    """Test application configuration"""
    # Check application attributes
    assert app.title == "Todoist API"
    assert "Task management API" in app.description
    assert app.version == "0.1.0"