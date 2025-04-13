"""
E2E tests for health check endpoint.
"""
import logging
import time
from typing import Dict, Any

import pytest
import requests

logger = logging.getLogger(__name__)

def test_health_endpoint(api_session, base_url):
    """
    Test that the health endpoint returns expected status and data.
    
    This test verifies:
    1. The endpoint returns a 200 status code
    2. The response contains the expected structure
    3. The database reports its status
    """
    logger.info(f"Testing health endpoint at {base_url}/health")
    
    # Make request to health endpoint
    response = api_session.get(f"{base_url}/health")
    
    # Log detailed response information
    logger.info(f"Health check response: {response.status_code}")
    logger.info(f"Response content: {response.text[:200]}")  # Limit log size
    
    # Check status code
    assert response.status_code == 200, f"Expected 200 status code, got {response.status_code}"
    
    # Check response structure
    data = response.json()
    assert "status" in data, "Response missing 'status' field"
    assert "database" in data, "Response missing 'database' field"
    
    # Check specific values
    assert data["status"] == "ok", f"Expected status 'ok', got '{data['status']}'"
    
    # Check database connection status exists (accept both connected or disconnected)
    assert data["database"] in ["connected", "disconnected"], f"Database status should be 'connected' or 'disconnected', got '{data['database']}'"
    
    logger.info(f"Health check E2E test passed successfully. Database status: {data['database']}")

def test_health_endpoint_response_time(api_session, base_url):
    """
    Test that the health endpoint responds within an acceptable time frame.
    
    For a health check, we expect very quick response times as this endpoint
    is used for monitoring and should be lightweight.
    """
    # Make request to health endpoint and measure time
    start_time = time.time()
    response = api_session.get(f"{base_url}/health")
    response_time = time.time() - start_time
    
    # Check response time is acceptable
    assert response.status_code == 200, "Health check should return 200 status code"
    assert response.elapsed.total_seconds() < 0.5, f"Health check response too slow: {response.elapsed.total_seconds()}s"
    
    logger.info(f"Health check response time: {response.elapsed.total_seconds():.3f}s")
