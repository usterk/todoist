# API Key generation & middleware

## Metadata
* **Ticket ID:** TICKET-003
* **Status:** backlog
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2023-11-27
* **Changed on:** 2023-11-27

## Description
Implement API key generation functionality and middleware for API key validation. This will allow external services to access the API without user-based authentication.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Implement POST /api/auth/apikey/generate endpoint
  - [ ] Add route and controller function
  - [ ] Generate unique API key
  - [ ] Store API key in database
  - [ ] Return API key to user
- [ ] Implement API key middleware
  - [ ] Extract API key from header
  - [ ] Validate API key against database
  - [ ] Check if key is revoked
  - [ ] Associate request with user
  - [ ] Return 401 if invalid
- [ ] Write tests
  - [ ] Test as much as possible with unit tests
  - [ ] Test all endpoints with e2e tests
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for the endpoint
  - [ ] Document API key usage
- [ ] Update project changelog

## Changelog
### [2023-11-27 14:00] - Ticket created
Initial ticket creation for API Key generation and middleware functionality.
