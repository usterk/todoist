# CRUD załączników (Attachments)

## Metadata
* **Ticket ID:** TASK-011
* **Status:** backlog
* **Priority:** medium
* **Assigned to:** copilot
* **Created on:** 2023-08-17
* **Changed on:** 2023-08-17

## Description
Implement complete CRUD operations for attachments associated with tasks. This functionality will allow users to store metadata about files linked to tasks, such as file paths or URLs pointing to external storage.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Create Attachments API endpoints
  - [ ] GET /api/tasks/:taskId/attachments - list all attachments for a task
  - [ ] GET /api/tasks/:taskId/attachments/:attachmentId - get single attachment details
  - [ ] POST /api/tasks/:taskId/attachments - create a new attachment
  - [ ] PUT /api/tasks/:taskId/attachments/:attachmentId - update an attachment
  - [ ] DELETE /api/tasks/:taskId/attachments/:attachmentId - delete an attachment
- [ ] Write tests
  - [ ] Unit tests for CRUD operations on attachments
  - [ ] Integration tests for attachments endpoints
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for all new endpoints
- [ ] Update project changelog

## Changelog
