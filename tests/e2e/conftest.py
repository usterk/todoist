"""
Configuration and fixtures for E2E tests.
"""

import os
import pytest
import requests
import time
import subprocess
import logging
from typing import Generator, Optional

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_BASE_URL = "http://localhost:5000"
MAX_RETRY_ATTEMPTS = 5
RETRY_WAIT_SECONDS = 2


def is_running_in_docker() -> bool:
    """
    Check if the code is running inside a Docker container.
    
    Returns:
        bool: True if running inside Docker, False otherwise
    """
    # Several ways to check, we'll use the existence of /.dockerenv
    return os.path.exists("/.dockerenv")


@pytest.fixture(scope="session")
def base_url() -> str:
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
    if is_running_in_docker():
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
    
    This is a placeholder - implement actual user creation when needed.
    Currently only used for tests that require authentication.
    """
    # This will be implemented in future tickets when working on auth tests
    return None
