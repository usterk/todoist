# API Key generation & middleware

## Metadata
* **Ticket ID:** TICKET-003
* **Status:** in_progress
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2023-11-27
* **Changed on:** 2023-11-28

## Description
Implement API key generation functionality and middleware for API key validation. This will allow external services to access the API without user-based authentication.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

### API Key Generation
1. Update the ApiKey model in app/models/user.py to ensure it has all required fields:
   - id (primary key)
   - user_id (foreign key to users table)
   - key_value (unique API key string)
   - description (optional description for the API key)
   - last_used (timestamp when the key was last used)
   - created_at (timestamp when the key was created)
   - revoked (boolean flag to indicate if the key is revoked)

2. Update the ApiKeyCreate and ApiKeyResponse schemas in app/schemas/user.py:
   - ApiKeyCreate: description field (optional)
   - ApiKeyResponse: id, key_value, description, created_at fields

3. Implement the generate_api_key function in app/api/auth.py:
   - Generate a secure random API key
   - Store the API key in the database with user association
   - Return the API key to the client

### API Key Middleware
1. Create an API key validation middleware:
   - Extract the API key from the x-api-key header
   - Look up the key in the database
   - Check if the key is revoked
   - Associate the user with the request
   - Return 401 Unauthorized if the key is invalid/revoked

2. Update the authentication flow to:
   - First check for JWT token in Authorization header
   - If no valid JWT token, check for API key in x-api-key header
   - Return 401 Unauthorized if both authentication methods fail

### Testing
1. Write comprehensive unit tests for:
   - API key generation functionality
   - API key validation
   - API key middleware

2. Write E2E tests that cover:
   - User login and API key generation
   - API endpoint access using API key authentication
   - API key revocation and subsequent authentication failure

## Tasks
- [x] Implement POST /api/auth/apikey/generate endpoint
  - [x] Add route and controller function
  - [x] Generate unique API key
  - [x] Store API key in database
  - [x] Return API key to user
- [x] Implement API key middleware
  - [x] Extract API key from header
  - [x] Validate API key against database
  - [x] Check if key is revoked
  - [x] Associate request with user
  - [x] Return 401 if invalid
- [x] Write tests
  - [x] Test as much as possible with unit tests
  - [x] Test all endpoints with e2e tests
- [x] Update documentation
  - [x] Add OpenAPI documentation for the endpoint
  - [x] Document API key usage
- [x] Update project changelog

## Changelog
### [2023-11-27 14:00] - Ticket created
Initial ticket creation for API Key generation and middleware functionality.

### [2023-11-28 09:00] - Ticket moved to in_progress
- Updated status to in_progress
- Added detailed implementation plan

### [2023-11-28 14:00] - Implementation completed
- Created unit tests for API key generation and middleware
- Implemented API key generation endpoint
- Implemented API key middleware for authentication
- Created API key revocation endpoint
- Added E2E tests for API key authentication
- Updated OpenAPI documentation for API key endpoints
