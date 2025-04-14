import pytest
import requests
import json
from urllib.parse import urljoin

def test_api_key_generation(base_url, api_session, auth_test_user):
    """Test generating an API key and using it for authentication."""
    # Login and get JWT token
    token = auth_test_user["token"]
    
    # Generate API key
    response = api_session.post(
        urljoin(base_url, "/api/auth/apikey/generate"),
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "E2E Test API Key"}
    )
    
    assert response.status_code == 201, f"Failed to generate API key: {response.text}"
    api_key_data = response.json()
    assert "key_value" in api_key_data
    assert "description" in api_key_data
    assert api_key_data["description"] == "E2E Test API Key"
    
    api_key = api_key_data["key_value"]
    
    # Use API key to access protected endpoint
    response = api_session.get(
        urljoin(base_url, "/api/users/me"),
        headers={"x-api-key": api_key}
    )
    
    assert response.status_code == 200, f"Failed to authenticate with API key: {response.text}"
    user_data = response.json()
    assert user_data["id"] == auth_test_user["id"]
    assert user_data["email"] == auth_test_user["email"]


def test_invalid_api_key(base_url, api_session):
    """Test that invalid API keys are rejected."""
    response = api_session.get(
        urljoin(base_url, "/api/users/me"),
        headers={"x-api-key": "invalid_api_key_value"}
    )
    
    assert response.status_code == 401, f"Expected 401 status code, got {response.status_code}"


def test_missing_api_key(base_url, api_session):
    """Test that missing API key results in authentication failure."""
    response = api_session.get(urljoin(base_url, "/api/users/me"))
    assert response.status_code == 401, f"Expected 401 status code, got {response.status_code}"


def test_api_key_generation_without_auth(base_url, api_session):
    """Test that generating an API key requires authentication."""
    response = api_session.post(
        urljoin(base_url, "/api/auth/apikey/generate"),
        json={"description": "Unauthorized attempt"}
    )
    
    assert response.status_code == 401, f"Expected 401 status code, got {response.status_code}"


def test_api_key_generation_and_revocation(base_url, api_session, auth_test_user):
    """Test full API key lifecycle: generation, use, revocation, and rejected use after revocation."""
    # Login and get JWT token
    token = auth_test_user["token"]
    
    # Generate API key
    response = api_session.post(
        urljoin(base_url, "/api/auth/apikey/generate"),
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Revocation Test Key"}
    )
    
    assert response.status_code == 201, f"Failed to generate API key: {response.text}"
    api_key_data = response.json()
    api_key = api_key_data["key_value"]
    api_key_id = api_key_data["id"]
    
    # Verify API key works
    response = api_session.get(
        urljoin(base_url, "/api/users/me"),
        headers={"x-api-key": api_key}
    )
    assert response.status_code == 200, f"Failed to authenticate with API key: {response.text}"
    
    # Revoke the API key
    response = api_session.post(
        urljoin(base_url, f"/api/auth/apikey/revoke/{api_key_id}"),
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Failed to revoke API key: {response.text}"
    
    # Verify API key no longer works
    response = api_session.get(
        urljoin(base_url, "/api/users/me"),
        headers={"x-api-key": api_key}
    )
    assert response.status_code == 401, f"Expected 401 for revoked API key, got {response.status_code}"
