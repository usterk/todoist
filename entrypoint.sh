#!/bin/bash
set -e

# Function to run tests with optional parameters
run_tests() {
  echo "🧪 Running tests..."
  
  # If no specific test path provided, run all tests
  if [ -z "$1" ]; then
    python -m pytest -v
  else
    # Run specific tests with any additional arguments
    python -m pytest -v "$@"
  fi
}

# Process the command
case "$1" in
  app)
    echo "🚀 Starting application with Uvicorn..."
    uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
    ;;
  test)
    # Remove the first argument (which is "test") and pass the rest to run_tests
    shift
    run_tests "$@"
    ;;
  shell)
    echo "🐚 Starting shell..."
    /bin/bash
    ;;
  *)
    echo "⚠️  Unknown command: $1"
    echo "Available commands:"
    echo "  app   - Run the application (default)"
    echo "  test  - Run tests (pytests)"
    echo "  shell - Start a shell"
    exit 1
    ;;
esac