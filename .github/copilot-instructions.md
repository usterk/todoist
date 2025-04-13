# Custom instructions for Copilot

## Project context
This project is a Python API application with comprehensive tests.
We use FastAPI for building RESTful APIs.
The application follows a modular structure with clear separation of concerns.

## Coding style
Follow PEP 8 style guidelines.
Use type hints for all function parameters and return values.
Keep functions small and focused on a single responsibility.
Use descriptive variable names in snake_case.
Include docstrings for all modules, classes, and functions.
Organize imports in three groups: standard library, third-party, local application.

## Testing
Use pytest as the primary testing framework.
Write unit tests for all business logic.
Include integration tests for API endpoints.
Aim for at least 80% code coverage.
Use fixtures to set up test environments.
Mock external dependencies when appropriate.

## Additional guidelines
Everything should be in English.
Keep code modular and reusable.
Prioritize readability and maintainability.
Follow the DRY (Don't Repeat Yourself) principle.
Handle errors explicitly with appropriate status codes and messages.
Include proper logging for debugging and monitoring.

## Ticket management
- Only work on tickets explicitly assigned to 'copilot'
- New tickets in backlog/ are initially assigned to copilot for initial analysis
- When ticket moves to in_progress/, wait for user to add implementation details
- Track progress in the Changelog section of ticket files
- Mark completed tasks with [x]
- Always create tests before completing any task
- When completed, change status to 'done' and move file to done/ directory

For complete ticket workflow details, see: tickets/README.md
