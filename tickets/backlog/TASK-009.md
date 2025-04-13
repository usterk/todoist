# CRUD etykiet (Labels)

## Metadata
* **Ticket ID:** TASK-009
* **Status:** backlog
* **Priority:** medium
* **Assigned to:** copilot
* **Created on:** 2023-08-17
* **Changed on:** 2023-08-17

## Description
Implement complete CRUD operations for labels (tags) that can be attached to tasks. This includes creating API endpoints for managing labels and the association between tasks and labels.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Create Labels API endpoints
  - [ ] GET /api/labels - list all labels
  - [ ] GET /api/labels/:labelId - get single label details
  - [ ] POST /api/labels - create a new label
  - [ ] PUT /api/labels/:labelId - update a label
  - [ ] DELETE /api/labels/:labelId - delete a label
- [ ] Implement Task-Label association endpoints
  - [ ] POST /api/tasks/:taskId/labels/:labelId - attach label to task
  - [ ] DELETE /api/tasks/:taskId/labels/:labelId - detach label from task
- [ ] Write tests
  - [ ] Unit tests for CRUD operations on labels
  - [ ] Integration tests for attaching/detaching labels to tasks
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for all new endpoints
- [ ] Update project changelog

## Changelog
