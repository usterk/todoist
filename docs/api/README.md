REST API specification
⸻

1. Authentication

You may secure these endpoints with JWT or sessions, and API keys for external integrations.

1.1 Register

POST /api/auth/register

Request Body (JSON):

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "someStrongPassword"
}

Response:
	•	201 Created: returns the created user's basic info (id, username, email).
	•	400 Bad Request: if fields are missing or user already exists.

1.2 Login

POST /api/auth/login

Request Body (JSON):

{
  "email": "john@example.com",
  "password": "someStrongPassword"
}

Response:
	•	200 OK: returns an auth token or session info.
	•	401 Unauthorized: wrong credentials.

1.3 Logout (Optional)

POST /api/auth/logout

	•	Invalidates the user session or JWT token.

1.4 Generate API Key

POST /api/auth/apikey/generate

Headers:
	•	Authorization: Bearer <JWT_TOKEN> (only authenticated users can generate API keys)

Response:
	•	200 OK: returns a newly generated API key.

Example Response:
```
{
  "api_key": "abcdef1234567890"
}
```

1.5 List API Keys

GET /api/auth/apikey

Headers:
	•	Authorization: Bearer <JWT_TOKEN>

Response:
	•	200 OK: returns a list of active API keys for the authenticated user.

1.6 Revoke API Key

DELETE /api/auth/apikey/:keyId

Headers:
	•	Authorization: Bearer <JWT_TOKEN>

Response:
	•	204 No Content: API key has been revoked.

1.7 Authentication Methods

There are two methods to authenticate API requests:

a) JWT Authentication:
	•	Include the JWT token in the Authorization header:
	•	Authorization: Bearer <JWT_TOKEN>

b) API Key Authentication:
	•	Include the API key in a custom header:
	•	x-api-key: <API_KEY>

Note: All endpoints (except registration/login) require either a valid JWT or a valid API Key.

⸻

2. Users

Use these if you want to manage multiple users (up to 5–10, as specified).

2.1 Get All Users

GET /api/users

	•	Returns a paginated or full list of users.

2.2 Get Single User

GET /api/users/:userId

	•	Returns user details for a given :userId.

2.3 Update User

PUT /api/users/:userId

Request Body (JSON) (all fields optional):

{
  "username": "newName",
  "email": "newEmail@example.com",
  "password": "newStrongPassword"
}

	•	200 OK: user updated.
	•	404 Not Found: user doesn’t exist.

2.4 Delete User

DELETE /api/users/:userId

	•	204 No Content: user deleted.
	•	404 Not Found: user doesn’t exist.

⸻

3. Projects

Projects group tasks at a high level.

3.1 Create Project

POST /api/projects

Request Body (JSON):

{
  "name": "My Project",
  "description": "Optional project details"
}

	•	201 Created: returns new project info.

3.2 List All Projects

GET /api/projects

	•	Returns an array of projects (with optional pagination).

3.3 Get Single Project

GET /api/projects/:projectId

	•	Returns detailed project info.

3.4 Update Project

PUT /api/projects/:projectId

Request Body (JSON) (all fields optional):

{
  "name": "Updated Project Name",
  "description": "Updated description"
}

	•	200 OK: project updated.
	•	404 Not Found: project not found.

3.5 Delete Project

DELETE /api/projects/:projectId

	•	204 No Content: project deleted.
	•	404 Not Found: project not found.

⸻

4. Sections

Sections further organize tasks inside a project.

4.1 Create Section

POST /api/projects/:projectId/sections

Request Body (JSON):

{
  "name": "Research Phase"
}

	•	201 Created: returns new section info under the project.

4.2 List All Sections in a Project

GET /api/projects/:projectId/sections

	•	Returns an array of sections.

4.3 Get Single Section

GET /api/projects/:projectId/sections/:sectionId

	•	Returns section details.

4.4 Update Section

PUT /api/projects/:projectId/sections/:sectionId

Request Body (JSON) (all fields optional):

{
  "name": "New Section Name"
}

	•	200 OK: section updated.
	•	404 Not Found: section not found.

4.5 Delete Section

DELETE /api/projects/:projectId/sections/:sectionId

	•	204 No Content: section deleted.
	•	404 Not Found: section not found.

⸻

5. Tasks

Core resource for the todo app. Tasks can be linked to projects, sections, and assigned to users.

5.1 Create Task

POST /api/tasks

Request Body (JSON):

{
  "project_id": 1,
  "section_id": 2,
  "assigned_to": 3,
  "title": "Complete the draft",
  "description": "Finish writing the first draft of the report",
  "priority": 2,
  "location": "Office Room #12",
  "due_date": "2025-04-30",       
  "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
  "reminder_datetime": "2025-04-29T10:00:00",
  "completed_at": null
}

Notes:
	•	project_id is required.
	•	section_id can be null if no sections are used.
	•	assigned_to (FK to users) if multi-user scenario is enabled.
	•	due_date can be updated later.
	•	recurrence_rule might be stored in RFC 5545 format.

Response:
	•	201 Created: returns created task.

5.2 List All Tasks

GET /api/tasks

	•	Returns an array of tasks (optionally filtered by project, user, etc. via query params).

Example:

GET /api/tasks?projectId=1&assignedTo=3

5.3 Get Single Task

GET /api/tasks/:taskId

	•	Returns a detailed task object.

5.4 Update Task

PUT /api/tasks/:taskId

Request Body (JSON) (all fields optional):

{
  "title": "Revised Title",
  "description": "Revised description",
  "priority": 1,
  "location": "Conference Room C",
  "due_date": "2025-05-01",
  "recurrence_rule": "FREQ=MONTHLY;BYDAY=1WE",
  "reminder_datetime": "2025-04-30T09:00:00",
  "completed_at": "2025-04-27T15:00:00"
}

	•	200 OK: task updated.
	•	404 Not Found: task not found.

5.5 Delete Task

DELETE /api/tasks/:taskId

	•	204 No Content: task deleted.
	•	404 Not Found: task not found.

⸻

6. Subtasks

Each task can have zero or more subtasks (checklist items).

6.1 Create Subtask

POST /api/tasks/:taskId/subtasks

Request Body (JSON):

{
  "title": "Write the introduction"
}

	•	201 Created: returns new subtask info.

6.2 List All Subtasks of a Task

GET /api/tasks/:taskId/subtasks

	•	Returns an array of subtasks belonging to the task.

6.3 Update Subtask

PUT /api/tasks/:taskId/subtasks/:subtaskId

Request Body (JSON):

{
  "title": "New subtask title",
  "completed_at": "2025-04-28T10:30:00"
}

	•	200 OK: subtask updated.

6.4 Delete Subtask

DELETE /api/tasks/:taskId/subtasks/:subtaskId

	•	204 No Content: subtask deleted.

⸻

7. Labels

Labels (tags) can be attached to tasks. Each label can be used on multiple tasks.

7.1 Create Label

POST /api/labels

Request Body (JSON):

{
  "name": "Urgent"
}

	•	201 Created: returns new label info.

7.2 List All Labels

GET /api/labels

	•	Returns an array of all labels.

7.3 Get Single Label

GET /api/labels/:labelId

	•	Returns a specific label.

7.4 Update Label

PUT /api/labels/:labelId

Request Body (JSON):

{
  "name": "Critical"
}

	•	200 OK: label updated.

7.5 Delete Label

DELETE /api/labels/:labelId

	•	204 No Content: label deleted.

7.6 Attach/Detach Label to Task

POST /api/tasks/:taskId/labels/:labelId

	•	Attaches a label to a task.

DELETE /api/tasks/:taskId/labels/:labelId

	•	Detaches a label from a task.

⸻

8. Attachments

File metadata is kept in the DB, actual files stored separately (e.g., AWS S3 or local folder).

8.1 Upload/Link Attachment

POST /api/tasks/:taskId/attachments

Request Body (JSON):

{
  "file_path": "http://example.com/files/report.pdf"
}

	•	201 Created: returns attachment info (id, file path).

8.2 List Attachments for a Task

GET /api/tasks/:taskId/attachments

	•	Returns an array of attachments for the task.

8.3 Delete Attachment

DELETE /api/tasks/:taskId/attachments/:attachmentId

	•	204 No Content: attachment metadata deleted.

⸻

9. Comments

Comments or notes on a task.

9.1 Create Comment

POST /api/tasks/:taskId/comments

Request Body (JSON):

{
  "comment": "We need more research here!"
}

	•	201 Created: returns the new comment.

9.2 List Comments for a Task

GET /api/tasks/:taskId/comments

	•	Returns an array of comments associated with the task.

9.3 Update Comment

PUT /api/tasks/:taskId/comments/:commentId

Request Body (JSON):

{
  "comment": "Updated comment text"
}

	•	200 OK: returns updated comment.

9.4 Delete Comment

DELETE /api/tasks/:taskId/comments/:commentId

	•	204 No Content: comment deleted.

⸻

10. Additional Considerations
	1.	Authentication & Authorization:
	•	You’d typically require a valid token (JWT) in headers (e.g., Authorization: Bearer <token>) to access these endpoints.
	•	Ensure that only the owner (or allowed users) can modify or delete their tasks, projects, etc.
	2.	Filtering & Searching:
	•	For tasks, consider query parameters like projectId, assignedTo, due_date, label, completed, etc.
	•	You can expand GET /api/tasks or create dedicated endpoints like /api/tasks/search.
	3.	Pagination:
	•	Commonly used for listing endpoints (GET /projects, GET /tasks).
	•	You can add query params like ?page=1&limit=20.
	4.	Timestamps:
	•	Typically returned in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ).
	•	The same format can be used in request bodies for date/time fields (due dates, reminder times, etc.).
	5.	Recurrence:
	•	Store recurrence rules in recurrence_rule using the iCalendar RRULE format.
	•	The server or client interprets and generates next due dates as needed.
	6.	Locations:
	•	If you want advanced location usage (e.g., geocoding, lat/long), replace the location string with more specific fields or store location data in a separate table.

⸻

Summary

This API structure covers users, projects, sections, tasks, subtasks, labels, attachments, and comments, aligning with the previously defined SQLite schema. You can adjust paths, naming conventions, and authentication logic as needed, but this design ensures CRUD operations for all core entities, plus the crucial relationships (e.g., tasks–labels, tasks–subtasks).
