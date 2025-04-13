# End-to-End (E2E) Testing Guide

This document describes the E2E testing approach for the Todoist API.

## Overview

End-to-End (E2E) tests validate the entire application stack by making HTTP requests to the API endpoints just as a real client would. These tests ensure that all components of the system work correctly together in a production-like environment.

Unlike unit tests that focus on isolated components, E2E tests verify complete user flows and real-world scenarios.

## Test Structure

Our E2E tests are organized in the `tests/e2e` directory with the following structure:

```
tests/e2e/
├── __init__.py
├── conftest.py           # Shared fixtures and configuration
├── test_health.py        # Tests for health endpoint
└── ... other test files
```

## Running E2E Tests

### Locally

To run all E2E tests:

```bash
./run.sh e2e-tests
```

To run a specific E2E test file:

```bash
./run.sh e2e-tests tests/e2e/test_health.py
```

### In CI/CD

E2E tests run automatically on GitHub Actions for:
- Pull requests to main branch
- Pushes to main branch

You can also trigger them manually through the GitHub Actions UI.

## Configuration

E2E tests can be configured using environment variables:

- `E2E_BASE_URL`: Base URL of the API (default: http://localhost:5000)
- `E2E_TESTING`: Flag indicating E2E test mode is active

## Writing E2E Tests

### Best Practices

1. **Independent tests**: Each test should be independent and not rely on state from other tests.
2. **Real-world scenarios**: Focus on testing complete user journeys rather than isolated functions.
3. **Minimal mocking**: Use real components whenever possible.
4. **Proper setup/teardown**: Clean up any created resources after tests.
5. **Resilient tests**: Account for real-world variability (network delays, etc.).

### Example Test

```python
def test_create_project(api_session, base_url, api_test_user):
    """Test creating a new project"""
    # Authenticate
    token = api_test_user["token"]
    
    # Create project
    response = api_session.post(
        f"{base_url}/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Test Project", "description": "E2E test"}
    )
    
    # Verify response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    
    # Verify project was created (GET request)
    project_id = data["id"]
    get_response = api_session.get(
        f"{base_url}/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Project"
```

## Test Data Management

For E2E tests, we need to handle test data carefully:

1. **Test users**: Create dedicated test users for E2E tests
2. **Cleanup**: Remove test data after tests complete
3. **Isolation**: Use unique identifiers (like UUIDs or timestamps) to ensure test data doesn't conflict

## Troubleshooting

If E2E tests fail:

1. Check if the API is running and accessible
2. Verify environment variables are set correctly
3. Look for detailed error messages in test output
4. Check API logs for server-side errors
5. Try running specific tests individually to isolate issues
