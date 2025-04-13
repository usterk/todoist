"""
Test script for local authentication verification.

This script tests JWT and API key authentication directly on the running API
without using the test framework. It's useful for quick verification that
the authentication is working as expected before running full test suite.
"""

import json
import pytest
import requests
import secrets
import string
import time
from typing import Dict, Any, Tuple

# Configuration
BASE_URL = "http://todoist-container:5000"  # Zmiana z localhost:5000 na todoist-container:5000

# Test fixtures
@pytest.fixture
def user_credentials() -> Tuple[str, str, str]:
    """Create unique user data for testing."""
    timestamp = int(time.time())
    random_str = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(8))
    username = f"testuser_{timestamp}_{random_str}"
    email = f"test_{timestamp}_{random_str}@example.com"
    password = "TestPassword123"
    return username, email, password


@pytest.fixture
def registered_user(user_credentials: Tuple[str, str, str]) -> Tuple[str, str, str]:
    """Register a test user and return credentials."""
    username, email, password = user_credentials
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    if response.status_code != 201:
        pytest.fail(f"Failed to register test user: {response.text}")
        
    return username, email, password


@pytest.fixture
def token(registered_user: Tuple[str, str, str]) -> str:
    """Get JWT token for registered user."""
    _, email, password = registered_user
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    if response.status_code != 200:
        pytest.fail(f"Failed to get token: {response.text}")
        
    data = response.json()
    return data["access_token"]


@pytest.fixture
def api_key(token: str) -> str:
    """Generate API key using JWT token."""
    response = requests.post(
        f"{BASE_URL}/api/auth/apikey/generate",
        json={"description": "Test API key"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code != 201:
        pytest.fail(f"Failed to generate API key: {response.text}")
        
    data = response.json()
    return data["key_value"]


def test_protected_endpoint_with_token(token: str) -> None:
    """Test protected endpoint with JWT token."""
    response = requests.get(
        f"{BASE_URL}/api/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Protected endpoint access failed: {response.status_code} - {response.text}"
    print(f"Protected endpoint response: {json.dumps(response.json(), indent=2)}")


def test_protected_endpoint_with_api_key(api_key: str) -> None:
    """Test protected endpoint with API key."""
    response = requests.get(
        f"{BASE_URL}/api/protected",
        headers={"x-api-key": api_key}
    )
    
    assert response.status_code == 200, f"Protected endpoint access failed: {response.status_code} - {response.text}"
    print(f"Protected endpoint response: {json.dumps(response.json(), indent=2)}")


def test_jwt_only_endpoint(token: str) -> None:
    """Test JWT-only endpoint."""
    response = requests.get(
        f"{BASE_URL}/api/protected/jwt-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"JWT-only endpoint access failed: {response.status_code} - {response.text}"
    print(f"JWT-only endpoint response: {json.dumps(response.json(), indent=2)}")


def test_api_key_only_endpoint(api_key: str) -> None:
    """Test API key-only endpoint."""
    response = requests.get(
        f"{BASE_URL}/api/protected/api-key-only",
        headers={"x-api-key": api_key}
    )
    
    assert response.status_code == 200, f"API key-only endpoint access failed: {response.status_code} - {response.text}"
    print(f"API key-only endpoint response: {json.dumps(response.json(), indent=2)}")