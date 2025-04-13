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
Create an endpoint for generating API keys and a middleware for validating API keys:

1. Implement POST /api/auth/apikey/generate endpoint:
   - This endpoint should be protected by JWT authentication
   - Generate a unique API key for the authenticated user
   - Store the API key in the database (api_keys table)
   - Return the generated API key to the user

2. Implement API key middleware:
   - Extract API key from x-api-key header
   - Validate the API key against the database
   - Check if the key has been revoked
   - If valid, associate the request with the corresponding user
   - If invalid, return 401 Unauthorized

3. Write comprehensive tests:
   - Test API key generation endpoint
   - Test API key middleware with valid and invalid keys
   - Test revoked key handling

4. Create OpenAPI documentation:
   - Document the API key generation endpoint
   - Include instructions on how to use API keys

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
  - [ ] Test API key generation
  - [ ] Test middleware with valid key
  - [ ] Test middleware with invalid key
  - [ ] Test middleware with revoked key
- [ ] Update documentation
  - [ ] Add OpenAPI documentation for the endpoint
  - [ ] Document API key usage
- [ ] Update project changelog

## Changelog
### [2023-11-27 14:00] - Ticket created
Initial ticket creation for API Key generation and middleware functionality.
