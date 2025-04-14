"""
E2E tests for authentication flows.
"""
import logging
import time
import random
import string
from typing import Dict, Optional, Tuple

import pytest
import requests

logger = logging.getLogger(__name__)


def create_unique_user_data() -> Tuple[str, str, str]:
    """
    Generate unique user data for tests to avoid conflicts.
    
    Returns:
        Tuple containing username, email, and password
    """
    # Use both timestamp and random string to ensure uniqueness
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
    username = f"testuser_{timestamp}_{random_str}"
    email = f"test_{timestamp}_{random_str}@example.com"
    password = "TestPassword123"
    return username, email, password


def create_test_user(api_session, base_url) -> Tuple[str, str, str]:
    """
    Helper function to create a test user for login and authentication tests.
    
    Returns:
        Tuple containing username, email, and password of the created user
    """
    # Generate unique credentials
    username, email, password = create_unique_user_data()
    
    # Try to register
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    # If registration succeeds, return credentials
    if response.status_code == 201:
        return username, email, password
    
    # If email already registered, try again with new credentials
    if response.status_code == 400 and "already registered" in response.text:
        logger.warning("Email or username already registered, trying again with new credentials")
        return create_test_user(api_session, base_url)
    
    # If some other error occurred, fail the test
    assert response.status_code == 201, f"Failed to create test user: {response.text}"
    return username, email, password


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


def get_api_key(api_session, base_url, token: str) -> str:
    """
    Helper function to generate an API key.
    
    Args:
        api_session: Session for API calls
        base_url: API base URL
        token: JWT token for authentication
        
    Returns:
        API key string
    """
    response = api_session.post(
        f"{base_url}/api/auth/apikey/generate",
        json={"description": "Test API key"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201, f"Failed to generate API key: {response.text}"
    data = response.json()
    assert "key_value" in data, "Response does not contain key_value"
    return data["key_value"]


def test_register_user_success(api_session, base_url):
    """
    Test successful user registration.
    
    This test verifies:
    1. The registration endpoint returns a 201 status code
    2. The response contains the expected user data
    3. The user can subsequently log in with the created credentials
    """
    # Generate unique credentials for this test
    username, email, password = create_unique_user_data()
    
    # Send registration request
    logger.info(f"Testing user registration with username: {username}")
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password
        }
    )
    
    # Verify the response status code and content
    assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}: {response.text}"
    
    # Check response data
    user_data = response.json()
    assert "id" in user_data, "Response should contain user ID"
    assert "username" in user_data, "Response should contain username"
    assert "email" in user_data, "Response should contain email"
    assert "created_at" in user_data, "Response should contain created_at timestamp"
    
    assert user_data["username"] == username, f"Expected username {username}, got {user_data['username']}"
    assert user_data["email"] == email, f"Expected email {email}, got {user_data['email']}"
    
    # Verify the user can log in with the registered credentials
    login_response = api_session.post(
        f"{base_url}/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    assert login_response.status_code == 200, f"Login failed after registration: {login_response.text}"
    login_data = login_response.json()
    assert "access_token" in login_data, "Login response should contain access token"
    assert login_data["token_type"] == "bearer", f"Expected token_type 'bearer', got {login_data['token_type']}"


def test_register_duplicate_email(api_session, base_url):
    """
    Test registration fails when using an email that is already registered.
    
    This test verifies:
    1. The first registration succeeds
    2. A second registration with the same email fails with a 400 status code
    """
    # Generate unique credentials for this test
    username1, email, password = create_unique_user_data()
    username2 = f"{username1}_duplicate"
    
    # First registration should succeed
    response1 = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username1,
            "email": email,
            "password": password
        }
    )
    
    assert response1.status_code == 201, f"First registration should succeed: {response1.text}"
    
    # Second registration with the same email should fail
    response2 = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username2,
            "email": email,
            "password": password
        }
    )
    
    assert response2.status_code == 400, f"Expected 400 Bad Request, got {response2.status_code}: {response2.text}"
    error_data = response2.json()
    assert "detail" in error_data, "Error response should contain detail field"
    assert "Email already registered" in error_data["detail"], f"Expected 'Email already registered' in error detail, got {error_data['detail']}"


def test_register_duplicate_username(api_session, base_url):
    """
    Test registration fails when using a username that is already taken.
    
    This test verifies:
    1. The first registration succeeds
    2. A second registration with the same username fails with a 400 status code
    """
    # Generate a unique username/email for the first registration
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email1 = f"test_{timestamp}_1@example.com"
    email2 = f"test_{timestamp}_2@example.com"
    password = "TestPassword123"
    
    # First registration should succeed
    response1 = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email1,
            "password": password
        }
    )
    
    assert response1.status_code == 201, f"First registration should succeed: {response1.text}"
    
    # Second registration with the same username should fail
    response2 = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email2,
            "password": password
        }
    )
    
    assert response2.status_code == 400, f"Expected 400 Bad Request, got {response2.status_code}: {response2.text}"
    error_data = response2.json()
    assert "detail" in error_data, "Error response should contain detail field"
    assert "Username already taken" in error_data["detail"], f"Expected 'Username already taken' in error detail, got {error_data['detail']}"


def test_register_invalid_password(api_session, base_url):
    """
    Test registration fails with invalid passwords.
    
    This test verifies password validation for:
    1. Password too short
    2. Password without uppercase letters
    3. Password without lowercase letters
    4. Password without digits
    """
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    email = f"test_{timestamp}@example.com"
    
    # Test password too short
    short_password = "Short1"
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": short_password
        }
    )
    assert response.status_code == 422, f"Expected 422 for short password, got {response.status_code}"
    
    # Test password without uppercase
    no_upper_password = "lowercase123"
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": no_upper_password
        }
    )
    assert response.status_code == 422, f"Expected 422 for no uppercase, got {response.status_code}"
    
    # Test password without lowercase
    no_lower_password = "UPPERCASE123"
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": no_lower_password
        }
    )
    assert response.status_code == 422, f"Expected 422 for no lowercase, got {response.status_code}"
    
    # Test password without digits
    no_digit_password = "NoDigitsHere"
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": no_digit_password
        }
    )
    assert response.status_code == 422, f"Expected 422 for no digits, got {response.status_code}"


def test_register_invalid_email(api_session, base_url):
    """
    Test registration fails when using an invalid email format.
    
    This test verifies:
    1. Registration with an invalid email format fails with a 422 status code
    """
    timestamp = int(time.time())
    username = f"testuser_{timestamp}"
    invalid_email = f"invalid_email_{timestamp}"  # Invalid email format
    password = "TestPassword123"
    
    response = api_session.post(
        f"{base_url}/api/auth/register",
        json={
            "username": username,
            "email": invalid_email,
            "password": password
        }
    )
    
    assert response.status_code == 422, f"Expected 422 Unprocessable Entity, got {response.status_code}: {response.text}"
    error_data = response.json()
    assert "detail" in error_data, "Error response should contain detail field"


def test_login_success(api_session, base_url):
    """
    Test successful login and token generation.
    
    This test verifies:
    1. User can register successfully
    2. User can log in with correct credentials
    3. Login response contains a valid JWT token
    """
    # Create a test user
    username, email, password = create_test_user(api_session, base_url)
    
    # Attempt login
    response = api_session.post(
        f"{base_url}/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    # Verify the response
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "access_token" in data, "Login response should contain access_token"
    assert "token_type" in data, "Login response should contain token_type"
    assert data["token_type"] == "bearer", f"Expected token_type 'bearer', got {data['token_type']}"
    
    # Verify token is in the correct format (JWT tokens have 3 parts separated by dots)
    token = data["access_token"]
    assert len(token.split('.')) == 3, f"Token does not appear to be a valid JWT: {token}"


def test_login_invalid_credentials(api_session, base_url):
    """
    Test login fails with invalid credentials.
    
    This test verifies:
    1. Login with incorrect password fails with 401 status code
    2. Login with non-existent email fails with 401 status code
    """
    # Create a test user
    username, email, password = create_test_user(api_session, base_url)
    
    # Test login with incorrect password
    response = api_session.post(
        f"{base_url}/api/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123"
        }
    )
    
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}: {response.text}"
    error_data = response.json()
    assert "detail" in error_data, "Error response should contain detail field"
    assert "Incorrect email or password" in error_data["detail"], f"Expected 'Incorrect email or password' in error detail, got {error_data['detail']}"
    
    # Test login with non-existent email
    non_existent_email = f"nonexistent_{int(time.time())}@example.com"
    response = api_session.post(
        f"{base_url}/api/auth/login",
        json={
            "email": non_existent_email,
            "password": password
        }
    )
    
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}: {response.text}"
    error_data = response.json()
    assert "detail" in error_data, "Error response should contain detail field"
    # Vague error message for security reasons (not confirming if email exists)
    assert "Incorrect email or password" in error_data["detail"], f"Expected 'Incorrect email or password' in error detail, got {error_data['detail']}"


def test_access_protected_endpoint_with_token(api_session, base_url):
    """
    Test accessing a protected endpoint using a valid JWT token.
    
    This test verifies:
    1. User can obtain a valid token through login
    2. Protected endpoints can be accessed with the token
    """
    # Create a test user and get token
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    # Try to access a protected endpoint
    response = api_session.get(
        f"{base_url}/api/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check that authentication works
    assert response.status_code == 200, f"Authentication failed with valid token: {response.text}"
    data = response.json()
    assert "user_id" in data, "Response should contain user_id"
    assert "username" in data, "Response should contain username"
    assert data["username"] == username, f"Expected username {username}, got {data['username']}"


def test_access_protected_endpoint_without_token(api_session, base_url):
    """
    Test accessing a protected endpoint without authentication.
    
    This test verifies:
    1. Protected endpoints return 401 Unauthorized when accessed without authentication
    """
    # Try to access a protected endpoint without authentication
    response = api_session.get(f"{base_url}/api/protected")
    
    # Check that authentication is required
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}: {response.text}"
    error_data = response.json()
    assert "detail" in error_data, "Error response should contain detail field"


def test_access_protected_endpoint_with_invalid_token(api_session, base_url):
    """
    Test accessing a protected endpoint with an invalid JWT token.
    
    This test verifies:
    1. Protected endpoints return 401 Unauthorized when accessed with an invalid token
    """
    # Try to access a protected endpoint with an invalid token
    response = api_session.get(
        f"{base_url}/api/protected",
        headers={"Authorization": "Bearer invalid.token.format"}
    )
    
    # Check that authentication fails with invalid token
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}: {response.text}"
    error_data = response.json()
    assert "detail" in error_data, "Error response should contain detail field"
    assert "Could not validate" in error_data["detail"], f"Expected 'Could not validate' in error detail, got {error_data['detail']}"


def test_api_key_authentication(api_session, base_url):
    """
    Test accessing a protected endpoint with an API key.
    
    This test verifies:
    1. User can generate an API key
    2. Protected endpoints can be accessed with the API key
    """
    # Create a test user and get token
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    # Generate an API key using the token
    api_key = get_api_key(api_session, base_url, token)
    
    # Try to access a protected endpoint with the API key
    response = api_session.get(
        f"{base_url}/api/protected",
        headers={"x-api-key": api_key}
    )
    
    # Check that authentication works with the API key
    assert response.status_code == 200, f"Authentication failed with valid API key: {response.text}"
    data = response.json()
    assert "user_id" in data, "Response should contain user_id"
    assert "username" in data, "Response should contain username"
    assert data["username"] == username, f"Expected username {username}, got {data['username']}"
    
    # Test API-key-only endpoint
    response = api_session.get(
        f"{base_url}/api/protected/api-key-only",
        headers={"x-api-key": api_key}
    )
    
    assert response.status_code == 200, f"API key authentication failed on API-key-only endpoint: {response.text}"
    data = response.json()
    assert data["auth_method"] == "API key", f"Expected auth_method 'API key', got {data.get('auth_method')}"


def test_api_key_invalid(api_session, base_url):
    """
    Test accessing a protected endpoint with an invalid API key.
    
    This test verifies:
    1. Protected endpoints return 401 Unauthorized when accessed with an invalid API key
    """
    # Try to access a protected endpoint with an invalid API key
    response = api_session.get(
        f"{base_url}/api/protected",
        headers={"x-api-key": "invalid-api-key-12345"}
    )
    
    # Check that authentication fails with invalid API key
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}: {response.text}"
    
    # Also check the API-key-only endpoint
    response = api_session.get(
        f"{base_url}/api/protected/api-key-only",
        headers={"x-api-key": "invalid-api-key-12345"}
    )
    
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}: {response.text}"
    error_data = response.json()
    assert "detail" in error_data, "Error response should contain detail field"


def test_jwt_only_endpoint(api_session, base_url):
    """
    Test accessing a JWT-only endpoint with JWT token.
    
    This test verifies:
    1. User can access endpoints requiring specifically JWT token
    2. JWT token permissions work as expected
    """
    # Create a test user and get token
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    # Try to access JWT-only endpoint with token
    response = api_session.get(
        f"{base_url}/api/protected/jwt-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check that authentication works
    assert response.status_code == 200, f"Authentication failed with valid JWT token: {response.text}"
    data = response.json()
    assert data["auth_method"] == "JWT token", "Response should specify JWT token auth method"
    assert data["username"] == username, f"Expected username {username}, got {data['username']}"


def test_jwt_only_endpoint_with_api_key(api_session, base_url):
    """
    Test accessing a JWT-only endpoint with API key.
    
    This test verifies:
    1. JWT-only endpoints reject API keys
    2. Proper authentication separation is maintained
    """
    # Create a test user, get token, then API key
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    api_key = get_api_key(api_session, base_url, token)
    
    # Try to access JWT-only endpoint with API key
    response = api_session.get(
        f"{base_url}/api/protected/jwt-only",
        headers={"x-api-key": api_key}
    )
    
    # Check that authentication fails (endpoint requires JWT)
    assert response.status_code == 401, f"Expected authentication to fail with API key on JWT-only endpoint"


def test_api_key_only_endpoint(api_session, base_url):
    """
    Test accessing an API key-only endpoint with API key.
    
    This test verifies:
    1. User can access endpoints requiring specifically API key
    2. API key permissions work as expected
    """
    # Create a test user and get API key
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    api_key = get_api_key(api_session, base_url, token)
    
    # Try to access API key-only endpoint
    response = api_session.get(
        f"{base_url}/api/protected/api-key-only",
        headers={"x-api-key": api_key}
    )
    
    # Check that authentication works with API key
    assert response.status_code == 200, f"Authentication failed with valid API key: {response.text}"
    data = response.json()
    assert data["auth_method"] == "API key", "Response should specify API key auth method"
    assert data["username"] == username, f"Expected username {username}, got {data['username']}"


def test_api_key_only_endpoint_with_jwt(api_session, base_url):
    """
    Test accessing an API key-only endpoint with JWT token.
    
    This test verifies:
    1. API key-only endpoints reject JWT tokens
    2. Proper authentication separation is maintained
    """
    # Create a test user and get token
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    # Try to access API key-only endpoint with JWT
    response = api_session.get(
        f"{base_url}/api/protected/api-key-only",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Check that authentication fails (endpoint requires API key)
    assert response.status_code == 401, f"Expected authentication to fail with JWT on API key-only endpoint"


def test_api_key_revocation(api_session, base_url):
    """
    Test revoking an API key.
    
    This test verifies:
    1. User can generate an API key
    2. User can revoke the API key
    3. Revoked API key is no longer valid for authentication
    """
    # Create a test user and get token and API key
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    # Generate API key
    response = api_session.post(
        f"{base_url}/api/auth/apikey/generate",
        json={"description": "Test API key for revocation"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201, f"Failed to generate API key: {response.text}"
    api_key_data = response.json()
    api_key = api_key_data["key_value"]
    api_key_id = api_key_data["id"]
    
    # Verify the API key works
    response = api_session.get(
        f"{base_url}/api/protected",
        headers={"x-api-key": api_key}
    )
    assert response.status_code == 200, f"API key authentication failed: {response.text}"
    
    # Revoke the API key
    response = api_session.post(
        f"{base_url}/api/auth/apikey/revoke/{api_key_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, f"Failed to revoke API key: {response.text}"
    
    # Try to use the revoked API key
    response = api_session.get(
        f"{base_url}/api/protected",
        headers={"x-api-key": api_key}
    )
    assert response.status_code == 401, f"Revoked API key should not be accepted: {response.text}"


@pytest.fixture(scope="function")
def auth_test_user(api_session, base_url) -> Dict[str, str]:
    """
    Create a test user with valid credentials and token for authentication tests.
    
    Returns:
        Dict with username, email, password, and token
    """
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    return {
        "username": username,
        "email": email,
        "password": password,
        "token": token
    }
