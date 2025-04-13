Tasker (clone) API

⸻

1. Overview

Product Name: Tasker API
Purpose: To provide a robust, secure, and scalable REST API for task management (projects, tasks, subtasks, labels, comments, attachments), supporting up to 5–10 users collaborating in small teams or individual use.
Key Differentiator: Flexible authentication with JWT (for user-based sessions) and API Keys (for external integrations or service accounts).

⸻

2. Goals & Objectives
	1.	Full CRUD over core task management entities:
	•	Projects and Sections
	•	Tasks and Subtasks
	•	Labels
	•	Comments
	•	Attachments (metadata)
	2.	Multi-User Collaboration (up to 5–10 users):
	•	Assign tasks to users
	•	Shared projects
	3.	Reminders & Recurring Tasks:
	•	Support due dates and recurrence rules (RRULE)
	•	Store reminders
	4.	Location:
	•	Basic field to store a task’s location
	5.	Advanced Filtering:
	•	Query tasks by project, label, assigned user, etc.
	6.	Security:
	•	JWT for user authentication (login-based).
	•	API Key generation for external services or integrations.
	7.	Scalability:
	•	Start with SQLite; potentially upgrade to PostgreSQL if needed.
	8.	Documentation:
	•	Clear, consistent API with predictable endpoints.

⸻

3. User Stories / Use Cases
	1.	User Authentication
	•	As a developer, I want to generate an API Key so that external services can access or manage tasks without a user-based token.
	•	As a registered user, I can sign up, log in, log out, and manage my session with a JWT.
	2.	Project & Sections
	•	As a team member, I want to create multiple projects and subdivide them into sections to keep tasks organized.
	3.	Task Management
	•	As a user, I can create tasks with due dates, priority, and location fields, optionally recurring, and assigned to myself or others.
	4.	Subtasks
	•	As a user, I can break down a single task into smaller action items (subtasks).
	5.	Labels
	•	As a user, I can group tasks with tags/labels for easier filtering.
	6.	Comments & Attachments
	•	As a collaborator, I can leave comments on tasks for discussion, and add file references (attachments).
	7.	Filtering & Searching
	•	As a user, I want to query tasks by label, project, assigned user, completion status, etc.

⸻

4. Functional Requirements

4.1 Authentication & Authorization
	•	JWT Authentication
	•	Register and Log in with email/password.
	•	Issue a JWT on successful login.
	•	Protect all authenticated endpoints with JWT in Authorization: Bearer <token>.
	•	API Key
	•	Generate an API key: a unique token associated with a user or a service account.
	•	Use x-api-key: <API_KEY> in headers for requests.
	•	Permission Handling:
	•	If using an API key, the same user restrictions apply (the key belongs to a certain user or service role).
	•	Potentially extend to role-based access if needed.

4.2 Projects & Sections
	•	Projects:
	•	Create, Read, Update, Delete projects.
	•	Each project has a name, optional description, created timestamp.
	•	Sections:
	•	Create, Read, Update, Delete sections under a project.
	•	Each section belongs to exactly one project.

4.3 Tasks & Subtasks
	•	Tasks:
	•	Create tasks with: title, description, priority, assigned user, due date, reminder datetime, location, recurrence rule, etc.
	•	Mark tasks complete (store completed_at).
	•	Move tasks between projects and sections.
	•	Subtasks:
	•	Create, Read, Update, Delete subtasks (checklist items).
	•	Mark subtasks as complete (completed_at).

4.4 Labels
	•	Labels:
	•	Create, Read, Update, Delete labels.
	•	Attach or detach labels from tasks (many-to-many relationship).

4.5 Comments & Attachments
	•	Comments:
	•	Create, Read, Update, Delete text-based comments associated with tasks.
	•	Attachments:
	•	Store metadata about files linked to tasks.
	•	Actual files stored externally (e.g., S3 or local filesystem); DB table holds file_path or URL.

4.6 Filtering & Searching
	•	Tasks can be filtered by query parameters:
	•	projectId=, assignedTo=, label=, completed=, due_date=, etc.

⸻

5. Non-Functional Requirements
	1.	Performance:
	•	API should respond under 500ms for typical requests.
	•	Proper indexing on frequently queried columns (e.g., due_date, assigned_to).
	2.	Security:
	•	Store passwords in hashed form (e.g., bcrypt).
	•	Validate JWT or API Key on each request.
	•	Restrict operations to the resource owner or authorized user.
	3.	Scalability:
	•	SQLite is fine for MVP; plan for migration to PostgreSQL if user/team size grows significantly.
	4.	Maintainability:
	•	Provide a consistent, versioned API (e.g., prefix routes with /api/v1).
	5.	Documentation:
	•	Deliver an OpenAPI/Swagger specification describing all endpoints and models.

⸻

6. Detailed Endpoint Descriptions

Below is the full endpoint list with HTTP methods, paths, parameters, and request/response structures.

Auth/Key Requirements:
	•	All endpoints (except registration/login) require either a valid JWT or a valid API Key header x-api-key.
	•	For brevity, we assume the same standard response codes:
	•	200 OK (success),
	•	201 Created (resource created),
	•	204 No Content (resource deleted or no body),
	•	400 Bad Request,
	•	401 Unauthorized,
	•	403 Forbidden,
	•	404 Not Found.

6.1 Authentication & Users

Register

POST /api/auth/register

Request Body (JSON):

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecretPass"
}

Response:
	•	201 Created with newly created user info (id, username, email).

Login

POST /api/auth/login

Request Body (JSON):

{
  "email": "john@example.com",
  "password": "SecretPass"
}

Response:

{
  "token": "<JWT_TOKEN>",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com"
  }
}

	•	200 OK if credentials are valid.
	•	401 Unauthorized if invalid.

Generate API Key

POST /api/auth/apikey/generate

Headers:
	•	Authorization: Bearer <JWT_TOKEN> (only authorized users can generate keys).

Response (JSON):

{
  "api_key": "abcdef1234567890"
}

	•	200 OK on success.

Use the returned key in subsequent requests:

x-api-key: abcdef1234567890

Logout (Optional)

POST /api/auth/logout

Response:
	•	200 OK or 204 No Content (depending on implementation).

Users (if needed beyond auth)

Get All Users

GET /api/users

Response (JSON array):

[
  {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "created_at": "2025-04-12T10:00:00"
  },
  ...
]

Get Single User

GET /api/users/:userId

Response:

{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "created_at": "2025-04-12T10:00:00"
}

Update User

PUT /api/users/:userId

Request Body (JSON) (all fields optional):

{
  "username": "newName",
  "email": "new@example.com",
  "password": "NewPass"
}

Delete User

DELETE /api/users/:userId



⸻

6.2 Projects

Create Project

POST /api/projects

Request Body:

{
  "name": "Marketing Campaign",
  "description": "Social media push"
}

Response:

{
  "id": 1,
  "name": "Marketing Campaign",
  "description": "Social media push",
  "created_at": "2025-04-12T12:34:56"
}

	•	201 Created

List Projects

GET /api/projects

Response (JSON array):

[
  {
    "id": 1,
    "name": "Marketing Campaign",
    "description": "Social media push"
  },
  ...
]

	•	200 OK

Get Single Project

GET /api/projects/:projectId

Response:

{
  "id": 1,
  "name": "Marketing Campaign",
  "description": "Social media push",
  "created_at": "2025-04-12T12:34:56"
}

	•	200 OK, 404 Not Found

Update Project

PUT /api/projects/:projectId

Request Body (optional fields):

{
  "name": "Updated Project Name",
  "description": "Revised description"
}

	•	200 OK, 404 Not Found

Delete Project

DELETE /api/projects/:projectId

	•	204 No Content, 404 Not Found

⸻

6.3 Sections

Create Section

POST /api/projects/:projectId/sections

Request Body:

{
  "name": "Research Section"
}

	•	201 Created

List Sections

GET /api/projects/:projectId/sections

Response (JSON array):

[
  {
    "id": 1,
    "project_id": 1,
    "name": "Research Section",
    "created_at": "2025-04-12T12:34:56"
  },
  ...
]

	•	200 OK

Get Single Section

GET /api/projects/:projectId/sections/:sectionId

	•	200 OK, 404 Not Found

Update Section

PUT /api/projects/:projectId/sections/:sectionId

Request Body:

{
  "name": "Competitive Analysis"
}

	•	200 OK, 404 Not Found

Delete Section

DELETE /api/projects/:projectId/sections/:sectionId

	•	204 No Content, 404 Not Found

⸻

6.4 Tasks

Create Task

POST /api/tasks

Request Body:

{
  "project_id": 1,
  "section_id": 2,
  "assigned_to": 3,
  "title": "Design Social Media Ads",
  "description": "Create mockups for Instagram and Facebook",
  "priority": 2,
  "location": "Office #5",
  "due_date": "2025-05-01",
  "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
  "reminder_datetime": "2025-04-30T09:00:00"
}

Response:

{
  "id": 10,
  "project_id": 1,
  "section_id": 2,
  "assigned_to": 3,
  "title": "Design Social Media Ads",
  "description": "Create mockups for Instagram and Facebook",
  "priority": 2,
  "location": "Office #5",
  "due_date": "2025-05-01",
  "recurrence_rule": "FREQ=WEEKLY;BYDAY=MO",
  "reminder_datetime": "2025-04-30T09:00:00",
  "completed_at": null,
  "created_at": "2025-04-12T12:40:00",
  "updated_at": "2025-04-12T12:40:00"
}

	•	201 Created

List Tasks

GET /api/tasks

Query Params:
	•	projectId, assignedTo, label, completed, etc.

Response (JSON array):

[
  {
    "id": 10,
    "title": "Design Social Media Ads",
    "project_id": 1,
    "section_id": 2,
    "priority": 2,
    "due_date": "2025-05-01",
    "completed_at": null
  },
  ...
]

	•	200 OK

Get Single Task

GET /api/tasks/:taskId

	•	200 OK, 404 Not Found

Update Task

PUT /api/tasks/:taskId

Request Body (all fields optional):

{
  "title": "Redesign Social Media Ads",
  "description": "Updated approach",
  "priority": 1,
  "due_date": "2025-05-02",
  "completed_at": "2025-04-30T10:00:00"
}

	•	200 OK, 404 Not Found

Delete Task

DELETE /api/tasks/:taskId

	•	204 No Content, 404 Not Found

⸻

6.5 Subtasks

Create Subtask

POST /api/tasks/:taskId/subtasks

Request Body:

{
  "title": "Write introduction copy"
}

	•	201 Created

List Subtasks

GET /api/tasks/:taskId/subtasks

	•	200 OK

Update Subtask

PUT /api/tasks/:taskId/subtasks/:subtaskId

Request Body:

{
  "title": "Review final introduction copy",
  "completed_at": "2025-04-15T10:00:00"
}

	•	200 OK

Delete Subtask

DELETE /api/tasks/:taskId/subtasks/:subtaskId

	•	204 No Content

⸻

6.6 Labels

Create Label

POST /api/labels

Request Body:

{
  "name": "Urgent"
}

	•	201 Created

List Labels

GET /api/labels

	•	200 OK

Get Single Label

GET /api/labels/:labelId

	•	200 OK, 404 Not Found

Update Label

PUT /api/labels/:labelId

Request Body:

{
  "name": "High Priority"
}

	•	200 OK, 404 Not Found

Delete Label

DELETE /api/labels/:labelId

	•	204 No Content, 404 Not Found

Attach Label to Task

POST /api/tasks/:taskId/labels/:labelId

	•	200 OK, or 201 Created with no body if you prefer

Detach Label from Task

DELETE /api/tasks/:taskId/labels/:labelId

	•	204 No Content

⸻

6.7 Comments

Create Comment

POST /api/tasks/:taskId/comments

Request Body:

{
  "comment": "We need a new color palette."
}

	•	201 Created

List Comments

GET /api/tasks/:taskId/comments

	•	200 OK

Update Comment

PUT /api/tasks/:taskId/comments/:commentId

Request Body:

{
  "comment": "Actually, let's finalize by Monday."
}

	•	200 OK

Delete Comment

DELETE /api/tasks/:taskId/comments/:commentId

	•	204 No Content

⸻

6.8 Attachments

Upload/Link Attachment

POST /api/tasks/:taskId/attachments

Request Body:

{
  "file_path": "http://storage.server.com/files/document.pdf"
}

	•	201 Created

List Attachments

GET /api/tasks/:taskId/attachments

	•	200 OK

Delete Attachment

DELETE /api/tasks/:taskId/attachments/:attachmentId

	•	204 No Content

⸻

7. Security & Authentication Flows
	1.	JWT Flow
	•	Registration → Login → Client stores token → Client sends token in Authorization header.
	•	Logout is optional (client-side token disposal or blacklisting token on server).
	2.	API Key Flow
	•	A user (already authenticated via JWT) calls POST /api/auth/apikey/generate.
	•	Server returns a unique token.
	•	Client (or external service) includes x-api-key: <token> in each request.
	•	The server checks validity and maps the API key to a specific user or service account.
	3.	Access Control
	•	Each request must pass either a valid JWT or a valid API key.
	•	The server enforces ownership and access rules (e.g., only the project owner or assigned user can update a task).

⸻

8. Success Metrics
	1.	Reliability: Minimal 5xx errors, robust error handling for invalid inputs.
	2.	Performance: Average response time < 500ms under typical loads.
	3.	Adoption: Clients easily integrate with the documented endpoints.
	4.	Security: No known vulnerabilities or security breaches; hashed passwords, protected endpoints.

⸻

9. Timeline (Example)
	1.	Phase 1 (Weeks 1–2):
	•	Set up DB schema (SQLite).
	•	Implement basic auth (register, login, user management).
	•	Projects & tasks (CRUD).
	2.	Phase 2 (Weeks 3–4):
	•	Subtasks, labels, comments, attachments.
	•	Implement API key generation.
	•	Recurrence rules & reminder storage.
	3.	Phase 3 (Week 5):
	•	Final checks, polishing, automated tests, documentation (OpenAPI/Swagger).
	•	Deploy MVP.

⸻

10. Open Questions / Future Considerations
	1.	Notification Service:
	•	Will the API send out emails/push notifications for reminders, or do we rely on external integrations?
	2.	Role-Based Access:
	•	Beyond “owner vs collaborator,” do we need advanced permissions (e.g., read-only, admin)?
	3.	File Upload Handling:
	•	Switch to direct file uploads to S3, or keep references only?

⸻
