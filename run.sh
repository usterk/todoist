#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  echo "📄 Loading environment variables from .env file..."
  # Use export to make variables available in this script
  export $(grep -v '^#' .env | xargs)
fi

# Parse arguments
# First argument is the command (app, test, shell, help)
COMMAND=${1:-"app"}
shift 1 || true  # Shift to remove the command from arguments

# Get project name from directory or environment variable
if [ -n "$PROJECT_NAME" ]; then
  DEFAULT_IMAGE_NAME="$PROJECT_NAME"
else
  # Extract project name from directory name
  DEFAULT_IMAGE_NAME=$(basename "$(pwd)")
fi

# Allow override of image name with APP_NAME env var
IMAGE_NAME=${APP_NAME:-$DEFAULT_IMAGE_NAME}
CONTAINER_NAME="$IMAGE_NAME-container"
APP_DIR=$(pwd)
HASH_FILE=".docker_build_hash"
PORT=5000
DATA_DIR="$APP_DIR/data"

# Display usage information if help requested
if [[ "$COMMAND" == "help" || "$COMMAND" == "--help" || "$COMMAND" == "-h" ]]; then
  echo "┌───────────────────────────────────────────────────────────────┐"
  echo "│ Usage:                                                        │"
  echo "│   ./run.sh [command] [args...]                               │"
  echo "│                                                               │"
  echo "│ Commands:                                                     │"
  echo "│   app   - Run the application (default)                       │"
  echo "│   test  - Run tests                                           │"
  echo "│   shell - Start a shell inside the container                  │"
  echo "│   help  - Display this help message                           │"
  echo "│                                                               │"
  echo "│ Environment Variables:                                        │"
  echo "│   APP_NAME     - Override the default image/container name    │"
  echo "│   PROJECT_NAME - Set the default project name                 │"
  echo "│                                                               │"
  echo "│ Configuration:                                                │"
  echo "│   .env file is automatically loaded if present                │"
  echo "│                                                               │"
  echo "│ Examples:                                                     │"
  echo "│   ./run.sh                  # Run app with default name       │"
  echo "│   ./run.sh test             # Run all tests                   │"
  echo "│   ./run.sh test tests/api/  # Run specific tests              │"
  echo "│   APP_NAME=myapp ./run.sh   # Run with custom name            │"
  echo "└───────────────────────────────────────────────────────────────┘"
  exit 0
fi

# Display info about the operation mode
if [[ "$COMMAND" == "app" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Running app with image name: $IMAGE_NAME        │"
  echo "└─────────────────────────────────────────────────┘"
elif [[ "$COMMAND" == "test" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Running tests with image name: $IMAGE_NAME      │"
  echo "└─────────────────────────────────────────────────┘"
elif [[ "$COMMAND" == "shell" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Starting shell with image name: $IMAGE_NAME     │"
  echo "└─────────────────────────────────────────────────┘"
fi

# Create data directory if it doesn't exist
if [ ! -d "$DATA_DIR" ]; then
  echo "📁 Creating data directory..."
  mkdir -p "$DATA_DIR"
fi

generate_hash() {
  cat Dockerfile requirements.txt entrypoint.sh | md5sum | cut -d' ' -f1
}

current_hash=$(generate_hash)
old_hash=""
if [ -f "$HASH_FILE" ]; then
  old_hash=$(cat "$HASH_FILE")
fi

# Check if container already exists
if docker ps -a | grep -q "$CONTAINER_NAME"; then
  echo "➡️ Stopping existing container..."
  docker stop "$CONTAINER_NAME" > /dev/null
  docker rm "$CONTAINER_NAME" > /dev/null
fi

# Build/rebuild image if needed
if [ "$current_hash" != "$old_hash" ]; then
  echo "🛠️ Changes detected in Dockerfile, requirements.txt, or entrypoint.sh - rebuilding image..."
  # Ensure entrypoint.sh has correct permissions
  chmod +x entrypoint.sh
  
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

echo "🚀 Starting container in $COMMAND mode..."

# Prepare the Docker command
DOCKER_ARGS="-it --name "$CONTAINER_NAME" -v "$APP_DIR:/app" -v "$DATA_DIR:/app/data" -e PYTHONPATH=/app -e DATA_DIRECTORY="/app/data""

# Pass environment variables from .env to container
if [ -f .env ]; then
  DOCKER_ARGS="$DOCKER_ARGS --env-file .env"
fi

# Add port mapping only when running the app
if [[ "$COMMAND" == "app" ]]; then
  DOCKER_ARGS="$DOCKER_ARGS -p $PORT:5000"
fi

# Run the container with the appropriate command
if [[ $# -gt 0 ]]; then
  # Run with additional arguments
  docker run $DOCKER_ARGS "$IMAGE_NAME" $COMMAND "$@"
else
  # Run with the basic command
  docker run $DOCKER_ARGS "$IMAGE_NAME" $COMMAND
fi

if [[ "$COMMAND" == "app" ]]; then
  echo "🛑 Application has been stopped"
elif [[ "$COMMAND" == "test" ]]; then
  echo "🧪 Test run completed"
elif [[ "$COMMAND" == "shell" ]]; then
  echo "🐚 Shell session ended"
fi