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
E2E_CONTAINER_NAME="$IMAGE_NAME-e2e-container"
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
  echo "│   app       - Run the application (default)                   │"
  echo "│   test      - Run all tests (unit, integration, and E2E)      │"
  echo "│   unit-test - Run only unit and integration tests             │"
  echo "│   e2e-test  - Start app and run E2E tests                     │"
  echo "│   shell     - Start a shell inside the container              │"
  echo "│   help      - Display this help message                       │"
  echo "│                                                               │"
  echo "│ Environment Variables:                                        │"
  echo "│   APP_NAME     - Override the default image/container name    │"
  echo "│   PROJECT_NAME - Set the default project name                 │"
  echo "│   E2E_BASE_URL - Base URL for E2E tests (default: local URL)  │"
  echo "│                                                               │"
  echo "│ Configuration:                                                │"
  echo "│   .env file is automatically loaded if present                │"
  echo "│                                                               │"
  echo "│ Examples:                                                     │"
  echo "│   ./run.sh                  # Run app with default name       │"
  echo "│   ./run.sh test             # Run all tests                   │"
  echo "│   ./run.sh unit-test        # Run unit and integration tests  │"
  echo "│   ./run.sh e2e-test         # Start app and run E2E tests     │"
  echo "│   APP_NAME=myapp ./run.sh   # Run with custom name            │"
  echo "└───────────────────────────────────────────────────────────────┘"
  exit 0
fi

# Display info about the operation mode
if [[ "$COMMAND" == "app" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Running app with image name: $IMAGE_NAME        │"
  echo "└─────────────────────────────────────────────────┐"
elif [[ "$COMMAND" == "test" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Running ALL tests with image name: $IMAGE_NAME  │"
  echo "└─────────────────────────────────────────────────┐"
elif [[ "$COMMAND" == "unit-test" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Running unit tests with image name: $IMAGE_NAME │"
  echo "└─────────────────────────────────────────────────┐"
elif [[ "$COMMAND" == "e2e-test" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Starting app and running E2E tests: $IMAGE_NAME │"
  echo "└─────────────────────────────────────────────────┐"
elif [[ "$COMMAND" == "shell" ]]; then
  echo "┌─────────────────────────────────────────────────┐"
  echo "│ Starting shell with image name: $IMAGE_NAME     │"
  echo "└─────────────────────────────────────────────────┐"
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

# Function to wait for API to be ready with better error handling and debugging
wait_for_api() {
  local MAX_ATTEMPTS=20
  local WAIT_TIME=5
  
  # First check if container is still running
  echo "⏳ Checking if API container is running..."
  if ! docker ps --filter "name=$CONTAINER_NAME" --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    echo "❌ API container is not running!"
    echo "📋 Container logs before exit:"
    docker logs "$CONTAINER_NAME"
    return 1
  fi
  
  # First check if the root endpoint is accessible (doesn't require DB)
  local ROOT_URL="http://localhost:$PORT/"
  echo "⏳ Waiting for API basic endpoint at $ROOT_URL"
  
  for ((i=1; i<=$MAX_ATTEMPTS; i++)); do
    echo "⏳ Attempt $i/$MAX_ATTEMPTS - Checking API root endpoint"
    
    # Use curl with verbose output for better debugging
    RESPONSE=$(curl -s "$ROOT_URL" 2>/dev/null)
    if [ $? -eq 0 ] && echo "$RESPONSE" | grep -q "message"; then
      echo "✅ Basic API endpoint is responding!"
      echo "$RESPONSE" | grep -o '"status":"[^"]*"'
      break
    fi
    
    echo "   API not responding yet..."
    
    # Show logs on each attempt
    echo "📋 Latest API logs:"
    docker logs --tail=20 "$CONTAINER_NAME"
    
    sleep $WAIT_TIME
  done
  
  # Then check if the health endpoint is accessible
  local API_URL="http://localhost:$PORT/health"
  echo "⏳ Waiting for API health endpoint at $API_URL"
  
  for ((i=1; i<=$MAX_ATTEMPTS; i++)); do
    echo "⏳ Attempt $i/$MAX_ATTEMPTS - Checking API health endpoint"
    
    # Use curl with verbose output for better debugging
    if RESPONSE=$(curl -s "$API_URL" 2>/dev/null); then
      if echo "$RESPONSE" | grep -q "status"; then
        echo "✅ API health endpoint is accessible!"
        echo "$RESPONSE"
        return 0
      fi
    fi
    
    echo "   Health endpoint not ready yet..."
    
    # Show logs on each attempt
    if [[ $i -gt 1 ]]; then
      echo "📋 Latest API logs:"
      docker logs --tail=10 "$CONTAINER_NAME"
    fi
    
    sleep $WAIT_TIME
  done
  
  echo "❌ Failed to access API health endpoint after $MAX_ATTEMPTS attempts"
  echo "📋 Full API container logs:"
  docker logs "$CONTAINER_NAME"
  
  # Even if health endpoint isn't ready, proceed if root endpoint is working
  # This allows testing to continue even if database initialization is incomplete
  if curl -s "$ROOT_URL" 2>/dev/null | grep -q "message"; then
    echo "⚠️ Warning: Health endpoint not ready, but root endpoint is working."
    echo "⚠️ Proceeding with tests, but some database-dependent tests may fail."
    return 0
  fi
  
  return 1
}

# Create Docker network if it doesn't exist
NETWORK_NAME="todoist_network"
if ! docker network inspect "$NETWORK_NAME" &> /dev/null; then
  echo "🌐 Creating Docker network: $NETWORK_NAME"
  docker network create "$NETWORK_NAME"
fi

# Run the container with the appropriate command
if [[ "$COMMAND" == "e2e-test" || "$COMMAND" == "e2e-tests" ]]; then
  # First, start the app in a detached container
  echo "🚀 Starting app in background..."
  APP_DOCKER_ARGS="-d --name "$CONTAINER_NAME" --network "$NETWORK_NAME" -v "$APP_DIR:/app" -v "$DATA_DIR:/app/data" -p $PORT:5000 -e PYTHONPATH=/app -e DATA_DIRECTORY="/app/data" -e PORT=5000"
  
  if [ -f .env ]; then
    APP_DOCKER_ARGS="$APP_DOCKER_ARGS --env-file .env"
  fi
  
  # Remove any existing containers to avoid conflicts
  docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
  
  # Start the API container
  docker run $APP_DOCKER_ARGS "$IMAGE_NAME" app
  
  # Give the container a moment to start before checking
  echo "⏳ Giving container time to initialize..."
  sleep 5
  
  # Wait for API to be fully operational
  wait_for_api || { 
    echo "❌ Failed to start the API! Stopping containers..."; 
    docker stop "$CONTAINER_NAME" > /dev/null 2>&1;
    docker rm "$CONTAINER_NAME" > /dev/null 2>&1;
    exit 1;
  }
  
  # Then run the E2E tests in a separate container
  echo "🧪 Running E2E tests..."
  # Remove any existing test containers
  docker rm -f "$E2E_CONTAINER_NAME" 2>/dev/null || true
  
  E2E_DOCKER_ARGS="-it --name "$E2E_CONTAINER_NAME" --network "$NETWORK_NAME" -v "$APP_DIR:/app" -e PYTHONPATH=/app -e E2E_TESTING=true -e E2E_BASE_URL=http://$CONTAINER_NAME:5000 -e API_CONTAINER_NAME=$CONTAINER_NAME"
  
  if [[ $# -gt 1 ]]; then
    # Run specific E2E test files if provided
    docker run $E2E_DOCKER_ARGS "$IMAGE_NAME" e2e-tests "${@:2}"
  else
    # Run all E2E tests
    docker run $E2E_DOCKER_ARGS "$IMAGE_NAME" e2e-tests
  fi
  
  # Clean up both containers
  echo "🧹 Cleaning up containers..."
  docker stop "$CONTAINER_NAME" > /dev/null
  docker rm "$CONTAINER_NAME" "$E2E_CONTAINER_NAME" > /dev/null

elif [[ "$COMMAND" == "test" ]]; then
  # Run ALL tests (unit, integration, and E2E)
  echo "🧪 Running all tests..."
  
  # First start the app for E2E tests
  echo "🚀 Starting app in background for E2E tests..."
  APP_DOCKER_ARGS="-d --name "$CONTAINER_NAME" --network "$NETWORK_NAME" -v "$APP_DIR:/app" -v "$DATA_DIR:/app/data" -p $PORT:5000 -e PYTHONPATH=/app -e DATA_DIRECTORY="/app/data" -e PORT=5000"
  
  if [ -f .env ]; then
    APP_DOCKER_ARGS="$APP_DOCKER_ARGS --env-file .env"
  fi
  
  docker run $APP_DOCKER_ARGS "$IMAGE_NAME" app
  
  # Give the container a moment to start before checking
  sleep 2
  
  # Wait for API to be fully operational
  wait_for_api || { 
    echo "❌ Failed to start the API! Stopping containers..."; 
    docker stop "$CONTAINER_NAME" > /dev/null 2>&1;
    docker rm "$CONTAINER_NAME" > /dev/null 2>&1;
    exit 1;
  }
  
  # Run all tests in another container
  echo "🧪 Running all tests..."
  TEST_DOCKER_ARGS="-it --name "$E2E_CONTAINER_NAME" --network "$NETWORK_NAME" -v "$APP_DIR:/app" -e PYTHONPATH=/app -e E2E_TESTING=true -e E2E_BASE_URL=http://$CONTAINER_NAME:5000"
  
  if [[ $# -gt 0 ]]; then
    # Run specific test files if provided
    docker run $TEST_DOCKER_ARGS "$IMAGE_NAME" test "$@"
  else
    # Run ALL tests
    docker run $TEST_DOCKER_ARGS "$IMAGE_NAME" test
  fi
  
  # Clean up both containers
  echo "🧹 Cleaning up containers..."
  docker stop "$CONTAINER_NAME" > /dev/null
  docker rm "$CONTAINER_NAME" "$E2E_CONTAINER_NAME" > /dev/null
  
elif [[ "$COMMAND" == "unit-test" ]]; then
  # Run only unit and integration tests (exclude E2E tests)
  echo "🧪 Running unit and integration tests..."
  
  if [[ $# -gt 0 ]]; then
    # Run specific test files if provided
    docker run $DOCKER_ARGS "$IMAGE_NAME" unit-tests "$@"
  else
    # Run all tests except those in the E2E directory
    docker run $DOCKER_ARGS "$IMAGE_NAME" unit-tests
  fi
  
elif [[ $# -gt 0 ]]; then
  # Run with additional arguments
  docker run $DOCKER_ARGS "$IMAGE_NAME" $COMMAND "$@"
else
  # Run with the basic command
  docker run $DOCKER_ARGS "$IMAGE_NAME" $COMMAND
fi

if [[ "$COMMAND" == "app" ]]; then
  echo "🛑 Application has been stopped"
elif [[ "$COMMAND" == "test" ]]; then
  echo "🧪 All test runs completed"
elif [[ "$COMMAND" == "unit-test" ]]; then
  echo "🧪 Unit test run completed"
elif [[ "$COMMAND" == "e2e-test" ]]; then
  echo "🧪 E2E test run completed" 
elif [[ "$COMMAND" == "shell" ]]; then
  echo "🐚 Shell session ended"
fi