# Zaawansowane filtrowanie

## Metadata
* **Ticket ID:** TASK-012
* **Status:** backlog
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2023-08-17
* **Changed on:** 2023-08-17

## Description
Enhance the GET /api/tasks endpoint to support advanced filtering capabilities. This will allow users to filter tasks by multiple criteria including project, assigned user, completion status, labels, due date ranges, and priority.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Extend GET /api/tasks endpoint with filtering parameters
  - [ ] Filter by project (projectId=X)
  - [ ] Filter by section (sectionId=X)
  - [ ] Filter by assigned user (assignedTo=X)
  - [ ] Filter by completion status (completed=true|false)
  - [ ] Filter by labels (label=X or labels=X,Y,Z)
  - [ ] Filter by due date (dueAfter=YYYY-MM-DD, dueBefore=YYYY-MM-DD)
  - [ ] Filter by priority (priority=1|2|3|4)
  - [ ] Support for combining multiple filters
- [ ] Implement pagination and sorting
  - [ ] Add limit and offset parameters
  - [ ] Add sortBy and sortDir parameters
- [ ] Write tests
  - [ ] Unit tests for filter combinations
  - [ ] Integration tests for filtering endpoints
  - [ ] Test edge cases (invalid parameters, out-of-range values)
- [ ] Update documentation
  - [ ] Add OpenAPI documentation with examples for filter usage
  - [ ] Create usage guide with common filter patterns
- [ ] Update project changelog

## Changelog
