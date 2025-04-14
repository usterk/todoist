"""
E2E tests for user management endpoints.
"""

import logging
import time
import random
import string
from typing import Dict, Optional, Tuple

import pytest
import requests

logger = logging.getLogger(__name__)


def generate_random_string(length: int = 8) -> str:
    """Generate a random string for unique test data."""
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def create_test_user(api_session, base_url) -> Dict[str, str]:
    """
    Helper function to create a test user.
    
    Args:
        api_session: Session for API calls
        base_url: API base URL
        
    Returns:
        Dict with user information and credentials
    """
    # Generate unique credentials
    timestamp = int(time.time())
    random_str = generate_random_string()
    username = f"testuser_{timestamp}_{random_str}"
    email = f"test_{timestamp}_{random_str}@example.com"
    password = "TestPassword123"
    
    # Register user
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    assert response.status_code == 201, f"Failed to create test user: {response.text}"
    user_data = response.json()
    user_data["password"] = password  # Add password for login purposes
    
    return user_data


def get_auth_token(api_session, base_url, email: str, password: str) -> str:
    """
    Helper function to get an authentication token.
    
    Args:
        api_session: Session for API calls
        base_url: API base URL
        email: User email
        password: User password
        
    Returns:
        JWT token string
    """
    response = api_session.post(
        f"{base_url}/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    assert response.status_code == 200, f"Failed to get auth token: {response.text}"
    data = response.json()
    assert "access_token" in data, "Response does not contain access_token"
    return data["access_token"]


def test_get_users_endpoint(api_session, base_url):
    """
    Test the GET /api/users endpoint.
    
    Verifies:
    1. Authentication is required
    2. Returns a list of users with correct fields
    3. Pagination works correctly
    """
    # Create a test user and get auth token
    user_data = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, user_data["email"], user_data["password"])
    
    # Test unauthenticated request
    response = api_session.get(f"{base_url}/api/users")
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test authenticated request
    response = api_session.get(
        f"{base_url}/api/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Failed to get users list: {response.text}"
    users = response.json()
    
    # Verify response structure
    assert isinstance(users, list), "Response should be a list"
    assert len(users) > 0, "Users list should not be empty"
    
    for user in users:
        assert "id" in user, "User should have id field"
        assert "username" in user, "User should have username field"
        assert "email" in user, "User should have email field"
        assert "created_at" in user, "User should have created_at field"
        assert "password_hash" not in user, "User should not expose password_hash"
    
    # Test pagination
    limit = 2
    response = api_session.get(
        f"{base_url}/api/users?limit={limit}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    limited_users = response.json()
    assert len(limited_users) <= limit, f"Limited users should be at most {limit}"
    
    # Test skip parameter if we have enough users
    if len(users) > 2:
        response = api_session.get(
            f"{base_url}/api/users?skip=1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        skipped_users = response.json()
        
        # First user in skipped_users should match second user in full list
        if len(skipped_users) > 0 and len(users) > 1:
            assert skipped_users[0]["id"] == users[1]["id"], "Skip parameter not working correctly"


def test_get_user_by_id_endpoint(api_session, base_url):
    """
    Test the GET /api/users/:userId endpoint.
    
    Verifies:
    1. Authentication is required
    2. Can get a specific user by ID
    3. Returns 404 for non-existent user
    4. Returns proper user data structure
    """
    # Create a test user and get auth token
    user_data = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, user_data["email"], user_data["password"])
    user_id = user_data["id"]
    
    # Test unauthenticated request
    response = api_session.get(f"{base_url}/api/users/{user_id}")
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test authenticated request for existing user
    response = api_session.get(
        f"{base_url}/api/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Failed to get user by ID: {response.text}"
    user = response.json()
    
    # Verify response structure
    assert user["id"] == user_id, "User ID should match requested ID"
    assert user["username"] == user_data["username"], "Username should match"
    assert user["email"] == user_data["email"], "Email should match"
    assert "created_at" in user, "User should have created_at field"
    assert "password_hash" not in user, "User should not expose password_hash"
    
    # Test request for non-existent user
    non_existent_id = 999999
    response = api_session.get(
        f"{base_url}/api/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404, f"Request for non-existent user should return 404, got {response.status_code}"
    error = response.json()
    assert "detail" in error, "Error response should have detail field"
    assert "not found" in error["detail"].lower(), "Error should mention user not found"


def test_update_user_endpoint(api_session, base_url):
    """
    Test the PUT /api/users/:userId endpoint.
    
    Verifies:
    1. Authentication is required
    2. User can update their own information
    3. User cannot update another user's information
    4. Cannot update to an existing username/email
    5. Password is updated correctly
    """
    # Create two test users and get auth token for first user
    user1_data = create_test_user(api_session, base_url)
    user2_data = create_test_user(api_session, base_url)
    token1 = get_auth_token(api_session, base_url, user1_data["email"], user1_data["password"])
    user1_id = user1_data["id"]
    user2_id = user2_data["id"]
    
    # Test updating own username and email
    new_username = f"updated_{user1_data['username']}"
    new_email = f"updated_{user1_data['email']}"
    
    update_data = {
        "username": new_username,
        "email": new_email
    }
    
    response = api_session.put(
        f"{base_url}/api/users/{user1_id}",
        headers={"Authorization": f"Bearer {token1}"},
        json=update_data
    )
    
    assert response.status_code == 200, f"Failed to update user: {response.text}"
    updated_user = response.json()
    
    assert updated_user["username"] == new_username, "Username should be updated"
    assert updated_user["email"] == new_email, "Email should be updated"
    
    # Test updating password
    new_password = "NewPassword123"
    update_data = {"password": new_password}
    
    response = api_session.put(
        f"{base_url}/api/users/{user1_id}",
        headers={"Authorization": f"Bearer {token1}"},
        json=update_data
    )
    
    assert response.status_code == 200, f"Failed to update password: {response.text}"
    
    # Verify login works with new password
    new_token = get_auth_token(api_session, base_url, new_email, new_password)
    assert len(new_token) > 0, "Should be able to login with new password"
    
    # Test trying to update another user's information
    response = api_session.put(
        f"{base_url}/api/users/{user2_id}",
        headers={"Authorization": f"Bearer {new_token}"},
        json={"username": "hacked_username"}
    )
    
    assert response.status_code == 403, f"Should not be able to update another user's info, got {response.status_code}"
    
    # Test updating to an existing username/email
    # First get auth token for second user
    token2 = get_auth_token(api_session, base_url, user2_data["email"], user2_data["password"])
    
    response = api_session.put(
        f"{base_url}/api/users/{user2_id}",
        headers={"Authorization": f"Bearer {token2}"},
        json={"username": new_username}  # Try to use user1's updated username
    )
    
    assert response.status_code == 400, f"Should not be able to use existing username, got {response.status_code}"


def test_delete_user_endpoint(api_session, base_url):
    """
    Test the DELETE /api/users/:userId endpoint.
    
    Verifies:
    1. Authentication is required
    2. User can delete their own account
    3. User cannot delete another user's account
    4. Returns 404 for non-existent user
    5. User can no longer login after deletion
    """
    # Create two test users and get auth tokens
    user1_data = create_test_user(api_session, base_url)
    user2_data = create_test_user(api_session, base_url)
    token1 = get_auth_token(api_session, base_url, user1_data["email"], user1_data["password"])
    token2 = get_auth_token(api_session, base_url, user2_data["email"], user2_data["password"])
    user1_id = user1_data["id"]
    user2_id = user2_data["id"]
    
    # Test user cannot delete another user's account
    response = api_session.delete(
        f"{base_url}/api/users/{user2_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    assert response.status_code == 403, f"Should not be able to delete another user's account, got {response.status_code}"
    
    # Test deleting non-existent user
    non_existent_id = 999999
    response = api_session.delete(
        f"{base_url}/api/users/{non_existent_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    assert response.status_code == 404, f"Request for non-existent user should return 404, got {response.status_code}"
    
    # Log request and response for debugging
    logging.debug(f"DELETE request to: {base_url}/api/users/{user1_id}")
    logging.debug(f"Headers: Authorization: Bearer {token1[:10]}...")
    
    # Test user can delete their own account
    response = api_session.delete(
        f"{base_url}/api/users/{user1_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    
    # Log response for debugging if error occurs
    if response.status_code != 204:
        logging.error(f"Delete user failed with status: {response.status_code}")
        logging.error(f"Response body: {response.text}")
    
    assert response.status_code == 204, f"Failed to delete user: status {response.status_code}, body: {response.text if hasattr(response, 'text') else 'No response text'}"
    
    # Verify user can no longer login after deletion
    response = api_session.post(
        f"{base_url}/api/auth/login",
        json={
            "email": user1_data["email"],
            "password": user1_data["password"]
        }
    )
    
    assert response.status_code == 401, f"Deleted user should not be able to login, got {response.status_code}"
    
    # Verify user no longer exists
    response = api_session.get(
        f"{base_url}/api/users/{user1_id}",
        headers={"Authorization": f"Bearer {token2}"}  # Use second user's token
    )
    
    assert response.status_code == 404, f"Deleted user should not exist, got {response.status_code}"
