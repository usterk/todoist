# CRUD komentarzy (Comments)

## Metadata
* **Ticket ID:** TASK-010
* **Status:** backlog
* **Priority:** medium
* **Assigned to:** copilot
* **Created on:** 2023-08-17
* **Changed on:** 2023-08-17

## Description
Implement complete CRUD operations for comments on tasks. This will allow users to add, view, edit, and delete comments on specific tasks, facilitating discussion and collaboration.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Create Comments API endpoints
  - [ ] GET /api/tasks/:taskId/comments - list all comments for a task
  - [ ] GET /api/tasks/:taskId/comments/:commentId - get single comment details
  - [ ] POST /api/tasks/:taskId/comments - create a new comment
  - [ ] PUT /api/tasks/:taskId/comments/:commentId - update a comment
  - [ ] DELETE /api/tasks/:taskId/comments/:commentId - delete a comment
- [ ] Write tests
  - [ ] Unit tests for CRUD operations on comments
  - [ ] Integration tests for comments endpoints
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for all new endpoints
- [ ] Update project changelog

## Changelog
