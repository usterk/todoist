# Role-based access control (RBAC)

## Metadata
* **Ticket ID:** TASK-019
* **Status:** backlog
* **Priority:** medium
* **Assigned to:** copilot
* **Created on:** 2023-08-19
* **Changed on:** 2023-08-19

## Description
Implement Role-Based Access Control (RBAC) to enhance application security by allowing fine-grained access control based on user roles. This will enable different permission levels for team members working on shared projects and tasks.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details

## Tasks
- [ ] Design RBAC system
  - [ ] Define role hierarchy (e.g., admin, manager, member, viewer)
  - [ ] Map permissions to resources and actions
  - [ ] Design role assignment structure
- [ ] Database schema updates
  - [ ] Create roles and permissions tables
  - [ ] Add user-role relationships
  - [ ] Add project-specific role assignments
- [ ] Implement core RBAC functionality
  - [ ] Create middleware for permission checking
  - [ ] Implement role and permission API
  - [ ] Add role assignment endpoints
- [ ] Update existing endpoints with permission checks
  - [ ] Add permission checks to project endpoints
  - [ ] Add permission checks to task endpoints
  - [ ] Update comments and attachments with permissions
- [ ] Create role management interface
  - [ ] APIs for creating and managing roles
  - [ ] Role assignment and revocation
  - [ ] Default role configuration
- [ ] Write tests
  - [ ] Test permission enforcement
  - [ ] Test role assignment and inheritance
  - [ ] Test access control edge cases
- [ ] Update documentation
  - [ ] Document RBAC system
  - [ ] Update API documentation with permission requirements
- [ ] Update project changelog

## Changelog
### [2023-08-19 14:00] - Ticket created
Initial ticket creation for Role-Based Access Control task.

# Implement End-to-End (E2E) Testing Framework

## Metadata
* **Ticket ID:** TASK-019
* **Status:** backlog
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2025-04-13
* **Changed on:** 2025-04-13

## Description
Implement a comprehensive end-to-end (E2E) testing framework for the Todoist API to ensure all API endpoints function correctly in a real-world environment. This will validate the complete user flows and integration between different components of the system, ensuring that the application works as expected from a user's perspective.

E2E tests will complement our existing unit and integration tests by verifying that all components work together properly, especially the authentication middleware, database operations, and business logic flows.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md
* API Documentation: /docs/api/README.md
* API Authentication Documentation: /docs/api/authentication.md

## Implementation Details

## Tasks
- [ ] Select and set up an E2E testing framework (suggested: Playwright or Cypress for API testing)
- [ ] Create a dedicated test environment configuration
  - [ ] Create a separate test database for E2E tests
  - [ ] Configure environment variables for test environment
- [ ] Implement E2E test suites for authentication flows
  - [ ] User registration
  - [ ] User login
  - [ ] JWT token authentication
  - [ ] API key authentication
- [ ] Implement E2E test suites for core functionality
  - [ ] Projects CRUD operations
  - [ ] Tasks CRUD operations
  - [ ] Labels and task categorization
  - [ ] Task assignment flows
- [ ] Implement E2E test suites for complex scenarios
  - [ ] Task recurrence and scheduling
  - [ ] Multi-user collaboration scenarios
  - [ ] Full user journey tests
- [ ] Update GitHub Actions configuration to run E2E tests
  - [ ] Create a separate workflow for E2E tests
  - [ ] Configure test database setup in CI environment
  - [ ] Set up proper reporting for test results
- [ ] Create helper utilities for test data management
  - [ ] Test data seeding scripts
  - [ ] Test data cleanup functions
- [ ] Document E2E testing approach and patterns
  - [ ] Update project README.md with E2E testing information
  - [ ] Create a dedicated E2E testing guide document
- [ ] Update tickets documentation
  - [ ] Update tickets/README.md to include E2E testing requirements
  - [ ] Update task templates to include E2E testing tasks
- [ ] Write tests
  - [ ] Unit tests for test helpers
  - [ ] E2E tests covering all critical user flows
- [ ] Update documentation
  - [ ] Create /docs/testing/e2e.md with detailed instructions
  - [ ] Update API documentation to include test examples
  - [ ] Add E2E testing section to project README.md
- [ ] Update project changelog

## Changelog
### [2025-04-13 13:15] - Ticket created
Initial ticket creation for implementing E2E testing framework. The task includes selecting a testing framework, creating test suites for various functionality, updating GitHub Actions configuration, and documenting the approach.
