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
    echo "🚀 Running application..."
    # Run with direct uvicorn command for better reliability
    # Set timeout to 120 seconds (much longer than default)
    PYTHONPATH=/app python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 --timeout-keep-alive 120
    ;;
  test)
    echo "🧪 Running tests..."
    python -m pytest -v
    ;;
  e2e-test|e2e-tests)
    echo "🧪 Running E2E tests..."
    if [ -n "$2" ]; then
        python -m pytest -xvs "$2"
    else
        python -m pytest -xvs tests/e2e
    fi
    ;;
  unit-test|unit-tests)
    echo "🧪 Running unit and integration tests..."
    python -m pytest -xvs -k "not e2e"
    ;;
  pytest)
    echo "🧪 Running pytest with custom arguments..."
    shift  # Remove the 'pytest' argument
    python -m pytest -xvs "$@"
    ;;
  shell)
    echo "🐚 Starting shell..."
    /bin/bash
    ;;
  *)
    echo "⚠️  Unknown command: $1"
    echo "Available commands:"
    echo "  app        - Run the application (default)"
    echo "  test       - Run tests (pytests)"
    echo "  e2e-tests  - Run end-to-end tests"
    echo "  unit-tests - Run unit and integration tests"
    echo "  pytest     - Run pytest with custom arguments"
    echo "  shell      - Start a shell"
    exit 1
    ;;
esac