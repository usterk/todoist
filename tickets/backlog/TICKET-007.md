# CRUD tasks

## Metadata
* **Ticket ID:** TICKET-007
* **Status:** backlog
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2023-11-27
* **Changed on:** 2023-11-27

## Description
Implement CRUD (Create, Read, Update, Delete) operations for tasks. Tasks are the core entity of the application and include a rich set of fields such as title, description, assignment, dates, location, and recurrence rules.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details
Create endpoints for managing tasks:

1. Implement POST /api/tasks endpoint:
   - Create new tasks with all supported fields (title, description, project_id, section_id, assigned_to, priority, location, due_date, recurrence_rule, reminder_datetime)
   - Validate input data including foreign key relationships
   - Return created task with ID

2. Implement GET /api/tasks endpoint:
   - Return a list of all tasks
   - Include pagination support
   - Support filtering by query parameters (projectId, assignedTo, completed, etc.)

3. Implement GET /api/tasks/:taskId endpoint:
   - Return a specific task by ID
   - Handle not found cases

4. Implement PUT /api/tasks/:taskId endpoint:
   - Update task information (all fields)
   - Validate input data
   - Return updated task info

5. Implement PATCH /api/tasks/:taskId/complete endpoint:
   - Mark a task as completed (set completed_at to current timestamp)
   - Return updated task info

6. Implement DELETE /api/tasks/:taskId endpoint:
   - Delete a task from the database
   - Handle associated resources (subtasks, comments, attachments, etc.)
   - Return appropriate status code

7. Write unit tests for all endpoints

8. Update OpenAPI documentation

## Tasks
- [ ] Implement POST /api/tasks endpoint
  - [ ] Create route and controller function
  - [ ] Validate input data including foreign keys
  - [ ] Return created task
- [ ] Implement GET /api/tasks endpoint
  - [ ] Create route and controller function
  - [ ] Add pagination support
  - [ ] Implement query parameter filtering
- [ ] Implement GET /api/tasks/:taskId endpoint
  - [ ] Create route and controller function
  - [ ] Handle not found cases
- [ ] Implement PUT /api/tasks/:taskId endpoint
  - [ ] Create route and controller function
  - [ ] Validate input data
  - [ ] Return updated task
- [ ] Implement PATCH /api/tasks/:taskId/complete endpoint
  - [ ] Create route and controller function
  - [ ] Set completed_at timestamp
  - [ ] Return updated task
- [ ] Implement DELETE /api/tasks/:taskId endpoint
  - [ ] Create route and controller function
  - [ ] Handle associated resources
  - [ ] Return appropriate status code
- [ ] Write tests
  - [ ] Test POST /api/tasks
  - [ ] Test GET /api/tasks
  - [ ] Test GET /api/tasks/:taskId
  - [ ] Test PUT /api/tasks/:taskId
  - [ ] Test PATCH /api/tasks/:taskId/complete
  - [ ] Test DELETE /api/tasks/:taskId
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for all endpoints
- [ ] Update project changelog

## Changelog
### [2023-11-27 16:00] - Ticket created
Initial ticket creation for task CRUD operations.
