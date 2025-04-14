# CRUD projects

## Metadata
* **Ticket ID:** TICKET-005
* **Status:** backlog
* **Priority:** medium
* **Assigned to:** copilot
* **Created on:** 2023-11-27
* **Changed on:** 2023-11-27

## Description
Implement CRUD (Create, Read, Update, Delete) operations for projects. This will allow users to manage their projects through the API.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details
Create endpoints for managing projects:

1. Implement POST /api/projects endpoint:
   - Create new projects with name and description
   - Validate input data
   - Return created project with ID

2. Implement GET /api/projects endpoint:
   - Return a list of all projects
   - Include pagination support

3. Implement GET /api/projects/:projectId endpoint:
   - Return a specific project by ID
   - Handle not found cases

4. Implement PUT /api/projects/:projectId endpoint:
   - Update project information (name, description)
   - Validate input data
   - Return updated project info

5. Implement DELETE /api/projects/:projectId endpoint:
   - Delete a project from the database
   - Handle associated resources (sections, tasks, etc.)
   - Return appropriate status code

6. Write unit tests for all endpoints

7. Update OpenAPI documentation

## Tasks
- [ ] Implement POST /api/projects endpoint
  - [ ] Create route and controller function
  - [ ] Validate input data
  - [ ] Return created project
- [ ] Implement GET /api/projects endpoint
  - [ ] Create route and controller function
  - [ ] Add pagination support
- [ ] Implement GET /api/projects/:projectId endpoint
  - [ ] Create route and controller function
  - [ ] Handle not found cases
- [ ] Implement PUT /api/projects/:projectId endpoint
  - [ ] Create route and controller function
  - [ ] Validate input data
  - [ ] Return updated project
- [ ] Implement DELETE /api/projects/:projectId endpoint
  - [ ] Create route and controller function
  - [ ] Handle associated resources
  - [ ] Return appropriate status code
- [ ] Write unit tests and e2e tests for all endpoints
- [ ] Run all tests
  - [ ] Fix test failures related to unique constraints
  - [ ] Fix issues with /api/users/me endpoint
  - [ ] Fix error in user deletion
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for all endpoints
- [ ] Update project changelog

## Changelog
### [2023-11-27 15:00] - Ticket created
Initial ticket creation for project CRUD operations.
