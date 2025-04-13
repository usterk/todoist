# TICKET-001: Project Structure and Database Setup

## Metadata
* **Ticket ID:** TICKET-001
* **Status:** done
* **Priority:** high
* **Assigned to:** copilot
* **Created on:** 2025-04-13
* **Changed on:** 2025-04-13

## Description
This task involves creating the basic structure for a task management API project, configuring the environment, and initial database setup. As the first step in application development, this ticket forms the foundational part upon which subsequent functionality will be built.

## Project Documentation References
* Database documentation: /docs/database/README.md and /docs/database/schema.md
* Product Requirements Document (PRD): /docs/PRD.md

## Implementation Details
The application should be configured to run in a Docker container with the following specifications:

1. **Environment Setup:**
   - Use a bash script (`run.sh`) to manage the container lifecycle
   - Implement an auto-rebuild feature when Dockerfile or requirements.txt changes
   - Mount the application directory and data directory as volumes

2. **Docker Configuration:**
   - Based on Python 3.9-slim image
   - Install dependencies from requirements.txt
   - Expose port 5000
   - Set appropriate environment variables

3. **Database Initialization:**
   - Initialize SQLite database on first application run
   - Create default admin user (username: admin, password: admin)
   - Implement database migrations using Alembic

4. **Running the Application:**
   - Start with `./run.sh [app-name]` command
   - Default app name should be "default-app" if not specified

**Example Files:**

**run.sh:**
```bash
#!/bin/bash

APP_NAME=${1:-"default-app"}
IMAGE_NAME="$APP_NAME"
CONTAINER_NAME="$APP_NAME-container"
APP_DIR=$(pwd)
HASH_FILE=".docker_build_hash"
PORT=5000
DATA_DIR="$APP_DIR/data"

# Display warning if no parameter was provided
if [ -z "$1" ]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ WARNING: No app name provided, using default-app │"
  echo "│ Usage: ./run.sh [app-name]                      │"
  echo "└─────────────────────────────────────────────────┘"
fi

# Create data directory if it doesn't exist
if [ ! -d "$DATA_DIR" ]; then
  echo "📁 Creating data directory..."
  mkdir -p "$DATA_DIR"
fi

generate_hash() {
  cat Dockerfile requirements.txt | md5sum | cut -d' ' -f1
}

current_hash=$(generate_hash)
old_hash=""
if [ -f "$HASH_FILE" ]; then
  old_hash=$(cat "$HASH_FILE")
fi

if docker ps -a | grep -q "$CONTAINER_NAME"; then
  echo "➡️ Stopping existing container..."
  docker stop "$CONTAINER_NAME" > /dev/null
  docker rm "$CONTAINER_NAME" > /dev/null
fi

if [ "$current_hash" != "$old_hash" ]; then
  echo "🛠️ Changes detected in Dockerfile or requirements.txt, rebuilding image..."
  docker build -t "$IMAGE_NAME" .

  if [ $? -eq 0 ]; then
    echo "$current_hash" > "$HASH_FILE"
    echo "✅ Docker image successfully built!"
  else
    echo "❌ Error building Docker image!"
    exit 1
  fi
else
  echo "✅ Using existing Docker image (no changes in configuration)"
fi

echo "🚀 Starting container with logs display..."
echo "📝 To stop the application, press Ctrl+C"

docker run -it \
  --name "$CONTAINER_NAME" \
  -p $PORT:5000 \
  -v "$APP_DIR:/app" \
  -v "$DATA_DIR:/app/data" \
  -e FLASK_APP=app.py \
  -e FLASK_ENV=development \
  -e DATA_DIRECTORY="/app/data" \
  "$IMAGE_NAME"

echo "🛑 Application has been stopped"
```

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# FastAPI application port
EXPOSE 5000

# Set environment variables
ENV PYTHONPATH=/app
ENV DATA_DIRECTORY=/app/data

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
```

## Tasks
- [x] Environment configuration
  - [x] Create run.sh script for Docker management
  - [x] Implement Dockerfile for Python 3.9
  - [x] Setup FastAPI configuration
- [x] Database structure
  - [x] Define DB schema (SQLite)
  - [x] Implement ORM (SQLAlchemy)
  - [x] Implement database initialization with default admin user
  - [x] Setup basic migration with Alembic
- [x] Basic endpoints
  - [x] Create health check endpoint (GET /health)
  - [x] Create basic authentication endpoints
- [x] Write tests
  - [x] Configuration tests
  - [x] Health check endpoint tests
  - [x] Database initialization tests
- [x] Update documentation
  - [x] Prepare README with setup instructions
  - [x] Document project structure
  - [x] Add usage examples
- [x] Update changelog

## Changelog
### [2025-04-13 14:30] - Work started
Task assigned to copilot. Implementation began with project structure setup.

### [2025-04-13 15:00] - Environment Configuration Completed
Created Dockerfile based on Python 3.9-slim and run.sh script for Docker container management. Set up appropriate environment variables and volume mounts.

### [2025-04-13 15:30] - Database Structure Implemented
Implemented SQLite database configuration with SQLAlchemy ORM. Created User model and database initialization logic that creates a default admin user.

### [2025-04-13 16:00] - Basic Endpoints Created
Implemented health check endpoint (GET /health) and authentication endpoints (register and login) with JWT token support.

### [2025-04-13 16:30] - Tests Written
Created tests for health check endpoint, database initialization, and authentication endpoints.

### [2025-04-13 17:00] - Documentation Updated
Updated README.md with project structure documentation, setup instructions, and usage examples.

### [2025-04-13 17:30] - Migration System with Alembic Added
Implemented Alembic migration system with initial schema migration. Integration with database initialization process complete. All tasks have been completed, marking ticket as done.
