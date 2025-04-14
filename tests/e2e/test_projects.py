"""
End-to-end tests for project API endpoints.
"""

import pytest
import time
import random
import string
from typing import Dict

def generate_random_string(length=8):
    """Generate a random string for test data uniqueness."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def create_test_project(api_session, base_url, token: str) -> Dict:
    """Create a test project and return its details."""
    project_name = f"test_project_{generate_random_string()}"
    project_description = f"Test project description {generate_random_string(16)}"
    
    response = api_session.post(
        f"{base_url}/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": project_name,
            "description": project_description
        }
    )
    
    assert response.status_code == 201, f"Failed to create test project: {response.text}"
    return response.json()

def test_create_project_endpoint(api_session, base_url, auth_test_user):
    """
    Test the POST /api/projects endpoint.
    
    Verifies:
    1. Authentication is required
    2. Can create a project with valid data
    3. Returns correct response structure
    4. Validates required fields
    """
    token = auth_test_user["token"]
    
    # Test unauthenticated request
    response = api_session.post(
        f"{base_url}/api/projects",
        json={"name": "Test Project", "description": "Test description"}
    )
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test authenticated request
    project_name = f"Test Project {generate_random_string()}"
    project_description = f"Test description {generate_random_string(16)}"
    
    response = api_session.post(
        f"{base_url}/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": project_name,
            "description": project_description
        }
    )
    
    assert response.status_code == 201, f"Failed to create project: {response.text}"
    project = response.json()
    assert project["name"] == project_name
    assert project["description"] == project_description
    assert "id" in project
    assert "created_at" in project
    
    # Test validation - missing required field (name)
    response = api_session.post(
        f"{base_url}/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Missing name field"}
    )
    assert response.status_code == 422, "Should validate required fields"

def test_get_projects_endpoint(api_session, base_url, auth_test_user):
    """
    Test the GET /api/projects endpoint.
    
    Verifies:
    1. Authentication is required
    2. Returns a list of projects with correct fields
    3. Pagination works correctly
    """
    token = auth_test_user["token"]
    
    # Create some test projects first
    for i in range(3):
        create_test_project(api_session, base_url, token)
    
    # Test unauthenticated request
    response = api_session.get(f"{base_url}/api/projects")
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test authenticated request
    response = api_session.get(
        f"{base_url}/api/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) >= 3  # We created at least 3 projects
    
    # Check project structure
    for project in projects:
        assert "id" in project
        assert "name" in project
        assert "description" in project
        assert "created_at" in project
    
    # Test pagination
    response = api_session.get(
        f"{base_url}/api/projects?limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) <= 2, "Pagination limit should be respected"
    
    # Test skip parameter
    response = api_session.get(
        f"{base_url}/api/projects?skip=1&limit=2",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    projects_skipped = response.json()
    assert len(projects_skipped) <= 2, "Pagination skip and limit should work together"

def test_get_project_by_id_endpoint(api_session, base_url, auth_test_user):
    """
    Test the GET /api/projects/:projectId endpoint.
    
    Verifies:
    1. Authentication is required
    2. Can get a specific project by ID
    3. Returns 404 for non-existent project
    4. Returns proper project data structure
    """
    token = auth_test_user["token"]
    
    # Create a test project
    project_data = create_test_project(api_session, base_url, token)
    project_id = project_data["id"]
    
    # Test unauthenticated request
    response = api_session.get(f"{base_url}/api/projects/{project_id}")
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test authenticated request
    response = api_session.get(
        f"{base_url}/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    project = response.json()
    assert project["id"] == project_id
    assert project["name"] == project_data["name"]
    assert project["description"] == project_data["description"]
    
    # Test non-existent project
    response = api_session.get(
        f"{base_url}/api/projects/9999999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404, "Should return 404 for non-existent project"

def test_update_project_endpoint(api_session, base_url, auth_test_user):
    """
    Test the PUT /api/projects/:projectId endpoint.
    
    Verifies:
    1. Authentication is required
    2. Can update a project
    3. Returns 404 for non-existent project
    4. Partial updates work correctly
    """
    token = auth_test_user["token"]
    
    # Create a test project
    project_data = create_test_project(api_session, base_url, token)
    project_id = project_data["id"]
    
    # Test unauthenticated request
    updated_name = f"Updated Project {generate_random_string()}"
    response = api_session.put(
        f"{base_url}/api/projects/{project_id}",
        json={"name": updated_name}
    )
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test full update
    updated_name = f"Updated Project {generate_random_string()}"
    updated_description = f"Updated description {generate_random_string(16)}"
    
    response = api_session.put(
        f"{base_url}/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": updated_name,
            "description": updated_description
        }
    )
    
    assert response.status_code == 200
    updated_project = response.json()
    assert updated_project["name"] == updated_name
    assert updated_project["description"] == updated_description
    
    # Test partial update (name only)
    new_name = f"New Name {generate_random_string()}"
    response = api_session.put(
        f"{base_url}/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": new_name}
    )
    
    assert response.status_code == 200
    partially_updated = response.json()
    assert partially_updated["name"] == new_name
    assert partially_updated["description"] == updated_description  # Should remain unchanged
    
    # Test updating non-existent project
    response = api_session.put(
        f"{base_url}/api/projects/9999999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "This project doesn't exist"}
    )
    
    assert response.status_code == 404, "Should return 404 for non-existent project"

def test_delete_project_endpoint(api_session, base_url, auth_test_user):
    """
    Test the DELETE /api/projects/:projectId endpoint.
    
    Verifies:
    1. Authentication is required
    2. Can delete a project
    3. Returns 404 for non-existent project
    4. Deleted project can no longer be retrieved
    """
    token = auth_test_user["token"]
    
    # Create a test project
    project_data = create_test_project(api_session, base_url, token)
    project_id = project_data["id"]
    
    # Test unauthenticated request
    response = api_session.delete(f"{base_url}/api/projects/{project_id}")
    assert response.status_code == 401, "Unauthenticated request should be denied"
    
    # Test deleting the project
    response = api_session.delete(
        f"{base_url}/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 204, "Delete should return 204 No Content"
    
    # Verify project is deleted
    response = api_session.get(
        f"{base_url}/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404, "Project should no longer exist after deletion"
    
    # Test deleting non-existent project
    response = api_session.delete(
        f"{base_url}/api/projects/9999999",  # Assuming this ID doesn't exist
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404, "Should return 404 for non-existent project"
