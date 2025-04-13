# Tasker API

Tasker API is a robust, secure, and scalable REST API for task management, supporting collaboration in small teams (5-10 users) or individual use.

## About the Project

Tasker API enables comprehensive task management, including:
- Full CRUD operations on projects, sections, tasks, and subtasks
- Labels, comments, and attachments
- Reminders and recurring tasks
- Multi-user collaboration

The key distinguishing features of the API are:
- Flexible authentication using JWT (for user sessions) and API Keys (for external integrations)
- Clear and predictable endpoints
- Advanced task filtering

## Project Structure

- `/app` - main application source code
- `/tests` - automated tests
- `/docs` - project documentation
- `/tickets` - development task management system

## Documentation

- **Product Requirements Document (PRD)**: [/docs/PRD.md](/docs/PRD.md)
- **Database Schema**: [/docs/database/schema.md](/docs/database/schema.md)

## Ticket Management System

The project uses a Markdown-based ticket system. A detailed description of the system, its structure, and workflow can be found in [/tickets/README.md](/tickets/README.md).

Tickets are organized in the following directories:
- `/tickets/backlog` - tasks waiting for implementation
- `/tickets/in_progress` - tasks in progress
- `/tickets/done` - completed tasks

## Installation and Running

```bash
./run.sh todoist
```

## Technologies

- FastAPI - framework for building APIs
- SQLAlchemy - ORM for database communication
- JWT - for user authentication
- Pytest - for automated testing

## License

This project is available under the [MIT](LICENSE) license.
