# CRUD subtasks

## Metadata
* **Ticket ID:** TICKET-008
* **Status:** backlog
* **Priority:** medium
* **Assigned to:** copilot
* **Created on:** 2023-11-27
* **Changed on:** 2023-11-27

## Description
Implement CRUD (Create, Read, Update, Delete) operations for subtasks. Subtasks allow users to break down tasks into smaller, more manageable items.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details
Create endpoints for managing subtasks:

1. Implement POST /api/tasks/:taskId/subtasks endpoint:
   - Create new subtasks under a specific task
   - Validate task existence
   - Return created subtask with ID

2. Implement GET /api/tasks/:taskId/subtasks endpoint:
   - Return a list of all subtasks for a specific task
   - Handle not found cases for invalid task IDs

3. Implement GET /api/tasks/:taskId/subtasks/:subtaskId endpoint:
   - Return a specific subtask by ID
   - Handle not found cases

4. Implement PUT /api/tasks/:taskId/subtasks/:subtaskId endpoint:
   - Update subtask information (title)
   - Validate input data
   - Return updated subtask info

5. Implement PATCH /api/tasks/:taskId/subtasks/:subtaskId/complete endpoint:
   - Mark a subtask as completed (set completed_at to current timestamp)
   - Return updated subtask info

6. Implement DELETE /api/tasks/:taskId/subtasks/:subtaskId endpoint:
   - Delete a subtask from the database
   - Return appropriate status code

7. Write unit tests for all endpoints

8. Update OpenAPI documentation

## Tasks
- [ ] Implement POST /api/tasks/:taskId/subtasks endpoint
  - [ ] Create route and controller function
  - [ ] Validate task existence
  - [ ] Return created subtask
- [ ] Implement GET /api/tasks/:taskId/subtasks endpoint
  - [ ] Create route and controller function
  - [ ] Handle not found cases for invalid task IDs
- [ ] Implement GET /api/tasks/:taskId/subtasks/:subtaskId endpoint
  - [ ] Create route and controller function
  - [ ] Handle not found cases
- [ ] Implement PUT /api/tasks/:taskId/subtasks/:subtaskId endpoint
  - [ ] Create route and controller function
  - [ ] Validate input data
  - [ ] Return updated subtask
- [ ] Implement PATCH /api/tasks/:taskId/subtasks/:subtaskId/complete endpoint
  - [ ] Create route and controller function
  - [ ] Set completed_at timestamp
  - [ ] Return updated subtask
- [ ] Implement DELETE /api/tasks/:taskId/subtasks/:subtaskId endpoint
  - [ ] Create route and controller function
  - [ ] Return appropriate status code
- [ ] Write unit tests and e2e tests for all endpoints
- [ ] Run all tests 
  - [ ] Ensure all tests pass
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for all endpoints
- [ ] Update project changelog

## Changelog
### [2023-11-27 16:15] - Ticket created
Initial ticket creation for subtask CRUD operations.
