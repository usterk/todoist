# SQLite Database Schema

This document details the database schema used in the Todoist application.

## Tables Overview
- [users](#users) - Stores user information
- [api_keys](#api_keys) - Stores API keys for external integrations
- [projects](#projects) - Represents projects to group tasks
- [sections](#sections) - Subdivisions within projects
- [tasks](#tasks) - Core table storing task details
- [subtasks](#subtasks) - Stores subtasks within tasks
- [labels](#labels) - Used to categorize tasks
- [task_labels](#task_labels) - Many-to-many relationship between tasks and labels
- [attachments](#attachments) - Stores metadata about task attachments
- [comments](#comments) - Stores notes or comments about tasks

## Table Definitions & Purposes

### users

Stores information about users who can be assigned tasks.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| username | TEXT | Username (unique) |
| email | TEXT | Email address (unique) |
| password_hash | TEXT | Hashed password for authentication |
| created_at | DATETIME | Timestamp user created |

### api_keys

Stores API keys for external integrations or service accounts.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| user_id | INTEGER | FK to users table - owner of the API key |
| key_value | TEXT | Unique API key value (hashed or encrypted) |
| description | TEXT | Optional description for the key |
| last_used | DATETIME | Timestamp when the key was last used |
| created_at | DATETIME | Timestamp when the key was created |
| revoked | BOOLEAN | Indicates if the key has been revoked |

### projects

Represents projects to group tasks logically.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Project name |
| description | TEXT | Project details (optional) |
| created_at | DATETIME | Timestamp |

### sections

Optional subdivisions (sections) within projects for deeper organization.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| project_id | INTEGER | FK to projects |
| name | TEXT | Section name |
| created_at | DATETIME | Timestamp |

### tasks

Core table storing task details.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| project_id | INTEGER | FK to projects |
| section_id | INTEGER | FK to sections (optional) |
| assigned_to | INTEGER | FK to users |
| title | TEXT | Task title |
| description | TEXT | Task details |
| priority | INTEGER | Priority (e.g., 1–4) |
| location | TEXT | Location associated with task |
| due_date | DATE | Specific due date |
| recurrence_rule | TEXT | Rule for repeating tasks (e.g. RFC RRULE format) |
| reminder_datetime | DATETIME | When to remind user |
| completed_at | DATETIME | Task completion timestamp |
| created_at | DATETIME | Timestamp |
| updated_at | DATETIME | Timestamp |

### subtasks

Stores subtasks (checklists) within tasks.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| task_id | INTEGER | FK to tasks |
| title | TEXT | Subtask description |
| completed_at | DATETIME | Completion timestamp |
| created_at | DATETIME | Timestamp |

### labels

Used to categorize tasks.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| name | TEXT | Label/tag name (unique) |
| created_at | DATETIME | Timestamp |

### task_labels

Many-to-many relationship between tasks and labels.

| Column | Type | Description |
|--------|------|-------------|
| task_id | INTEGER | FK to tasks |
| label_id | INTEGER | FK to labels |

### attachments

Stores metadata about attachments (actual files are in separate storage).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| task_id | INTEGER | FK to tasks |
| file_path | TEXT | Path or URL to the file |
| uploaded_at | DATETIME | Timestamp |

### comments

Stores textual notes or comments about tasks.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| task_id | INTEGER | FK to tasks |
| user_id | INTEGER | FK to users |
| comment | TEXT | Comment text |
| created_at | DATETIME | Timestamp |

## Relationships

- Each task belongs to a single project (mandatory) and optionally a section
- Tasks can have multiple subtasks, labels, attachments, and comments
- Labels can be associated with many tasks (many-to-many)
- Each task can be assigned to one user, but users can handle many tasks

## Recommended Indexes

For optimal performance, the following indexes are recommended:

- Foreign keys (project_id, section_id, task_id, user_id, label_id)
- Date/time fields (due_date, completed_at, reminder_datetime)
- Frequently queried fields (e.g., priority)

## Recurrence Rule Usage

The `recurrence_rule` field in the tasks table uses RFC 5545 RRULE format. Examples:

- Daily: `FREQ=DAILY`
- Weekly every Tuesday and Thursday: `FREQ=WEEKLY;BYDAY=TU,TH`
- Monthly on 1st Wednesday: `FREQ=MONTHLY;BYDAY=1WE`

## Summary

- Users can create and manage multiple projects, each containing optional sections to organize tasks better
- Each task can be richly described, assigned priorities, due dates, reminders, and set to recur according to complex rules
- Tasks support additional metadata through subtasks, labels, comments, and attachments (stored externally)
- Labels offer flexible categorization
- The database is optimized for efficient queries and clear relationships
