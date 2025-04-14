"""
Configuration and fixtures for E2E tests.
"""

import os
import pytest
import requests
import time
import subprocess
import logging
import random
import string
from typing import Generator, Optional, Dict, Tuple

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_BASE_URL = "http://localhost:5000"
MAX_RETRY_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 2


def pytest_addoption(parser):
    """Add custom command line options for e2e tests."""
    parser.addoption(
        "--skip-docker", 
        action="store_true", 
        default=False, 
        help="Skip Docker container checks, useful in CI environments"
    )


def is_running_in_docker(request=None) -> bool:
    """
    Check if the code is running inside a Docker container.
    
    Args:
        request: pytest request object (optional)
        
    Returns:
        bool: True if running inside Docker, False otherwise
    """
    # If --skip-docker is passed, always return False
    if request and request.config.getoption("--skip-docker", False):
        logger.info("--skip-docker option used, skipping Docker container checks")
        return False
    
    # Several ways to check, we'll use the existence of /.dockerenv
    return os.path.exists("/.dockerenv")


@pytest.fixture(scope="session")
def base_url(request) -> str:
    """
    Determine the base URL for E2E tests.
    
    This will use the environment variable E2E_BASE_URL if provided,
    otherwise it will use a default URL.
    """
    # Use environment variable if provided
    if os.environ.get("E2E_BASE_URL"):
        base_url = os.environ.get("E2E_BASE_URL")
        logger.info(f"Using environment-provided base URL: {base_url}")
        return base_url
    
    # If in Docker, use container name from environment or default
    if is_running_in_docker(request):
        container_name = os.environ.get("API_CONTAINER_NAME", "todoist_app")
        base_url = f"http://{container_name}:5000"
        logger.info(f"Using Docker container networking with URL: {base_url}")
        return base_url
    
    # Default for local development
    logger.info(f"Using default base URL: {DEFAULT_BASE_URL}")
    return DEFAULT_BASE_URL


@pytest.fixture(scope="session")
def api_session() -> Generator[requests.Session, None, None]:
    """
    Create a requests session for making API calls.
    
    This session is reused across tests to maintain efficiency.
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "E2ETest/1.0",
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    
    yield session
    
    # Clean up
    session.close()


@pytest.fixture(scope="session", autouse=True)
def ensure_api_running(base_url) -> None:
    """
    Ensure the API is running and accessible before running tests.
    """
    logger.info(f"Checking API availability at {base_url}")
    
    # Try to connect to API with increased timeout and retries
    for attempt in range(10):
        try:
            logger.info(f"API connection attempt {attempt+1}/10")
            # First try a simple root endpoint that doesn't require DB
            response = requests.get(f"{base_url}/", timeout=10)
            if response.status_code == 200:
                logger.info(f"Basic API endpoint is accessible: {response.json()}")
                
                # Then try the health endpoint, but don't fail if it's not ready
                try:
                    health_response = requests.get(f"{base_url}/health", timeout=10)
                    if health_response.status_code == 200:
                        logger.info(f"API health check succeeded: {health_response.json()}")
                    else:
                        logger.warning(f"API health check failed with status {health_response.status_code}")
                        logger.warning("Some database-dependent tests may fail")
                except requests.RequestException as e:
                    logger.warning(f"Health endpoint not accessible: {str(e)}")
                    logger.warning("Some database-dependent tests may fail")
                
                # Continue with tests even if health endpoint isn't ready yet
                return
            else:
                logger.warning(f"Basic API endpoint check failed: {response.status_code}")
        except requests.RequestException as e:
            logger.warning(f"Connection error on attempt {attempt+1}/10: {str(e)}")
        
        time.sleep(3)
    
    logger.error(f"Could not connect to API at {base_url} after 10 attempts")
    logger.error("Available environment variables:")
    for key, value in sorted(os.environ.items()):
        if not key.startswith(('PATH', 'PS', 'LESS', 'LC_', 'BASH')):
            logger.error(f"  {key}={value}")
    
    pytest.skip(f"API server not accessible at {base_url}")


@pytest.fixture(scope="function")
def api_test_user(api_session, base_url) -> Optional[dict]:
    """
    Create a test user for API testing.
    
    Creates a user with unique credentials for tests that require authentication.
    """
    # Use both timestamp and random string to ensure uniqueness
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_lowercase, k=8))
    username = f"testuser_{timestamp}_{random_str}"
    email = f"test_{timestamp}_{random_str}@example.com"
    password = "TestPassword123"
    
    try:
        # Register the user
        register_response = api_session.post(
            f"{base_url}/api/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        
        # Check if registration was successful
        if register_response.status_code != 201:
            logger.warning(f"Failed to create test user: {register_response.text}")
            return None
            
        # Log in to get authentication token
        login_response = api_session.post(
            f"{base_url}/api/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        
        # Check if login was successful
        if login_response.status_code != 200:
            logger.warning(f"Failed to log in with test user: {login_response.text}")
            return None
            
        login_data = login_response.json()
        token = login_data.get("access_token")
        
        if not token:
            logger.warning("Login response did not contain access token")
            return None
            
        # Return user details including token
        return {
            "id": register_response.json().get("id"),
            "username": username,
            "email": email,
            "password": password,
            "token": token
        }
            
    except Exception as e:
        logger.exception(f"Error creating test user: {str(e)}")
        return None


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


@pytest.fixture(scope="function")
def auth_test_user(api_session, base_url) -> Dict[str, str]:
    """
    Create a test user with valid credentials and token for authentication tests.
    
    Returns:
        Dict with username, email, password, and token
    """
    username, email, password = create_test_user(api_session, base_url)
    token = get_auth_token(api_session, base_url, email, password)
    
    # Get user ID by accessing the /api/users/me endpoint with the token
    user_response = api_session.get(
        f"{base_url}/api/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if user_response.status_code != 200:
        logger.warning(f"Failed to get user details: {user_response.text}")
        user_id = None
    else:
        user_id = user_response.json().get("id")
    
    return {
        "id": user_id,
        "username": username,
        "email": email,
        "password": password,
        "token": token
    }
