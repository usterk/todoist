# Todoist API

Task management application built with FastAPI and SQLite.

[![Codecov](https://codecov.io/gh/usterk/todoist/branch/master/graph/badge.svg)](https://codecov.io/gh/usterk/todoist)

## Project Structure

```
todoist/
├── app/                     # Application source code
│   ├── api/                 # API endpoints module
│   ├── auth/                # Authentication module
│   ├── core/                # Configuration and helper functions
│   ├── database/            # Database configuration and handling
│   ├── models/              # SQLAlchemy ORM models
│   └── schemas/             # Pydantic schemas for data validation
├── data/                    # Directory storing SQLite database
├── docs/                    # Project documentation
├── tests/                   # Unit and integration tests
├── Dockerfile               # Containerization configuration
├── requirements.txt         # Python dependencies
├── entrypoint.sh            # Entry script for the container
└── run.sh                   # Script to run the application in Docker
```

## Requirements

- Python 3.9+
- Docker
- Internet access to download dependencies

## Running the application

### Using Docker

You can run the application using the `run.sh` script, which automatically builds the Docker image and runs the container:

```bash
# Grant execute permissions to the script (only once)
chmod +x run.sh

# Run the application with the default name
./run.sh

# Or provide your own application name
./run.sh app my-application
```

The script automatically:
1. Detects changes in Dockerfile, requirements.txt, or entrypoint.sh and rebuilds the image if necessary
2. Stops and removes the existing container with the same name
3. Creates a directory for data if it does not exist
4. Runs the container with appropriate mounts for code and data

### Running tests in the container

You can run tests in the Docker container using the command:

```bash
# Run all tests
./run.sh test

# Run tests with the given application name
./run.sh test my-application

# Run specific tests or with additional parameters
./run.sh test my-application tests/api/
./run.sh test my-application -v tests/api/test_health.py
```

### Accessing the shell in the container

To access the bash shell inside the container:

```bash
./run.sh shell my-application
```

### Help

To display help for using the run.sh script:

```bash
./run.sh help
```

### Without Docker

If you prefer to run the application directly:

```bash
# Create and activate a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload

# Run tests
pytest
```

## Accessing the API

Once running, the API is available at:
- http://localhost:5000/

Swagger UI documentation:
- http://localhost:5000/docs

ReDoc documentation:
- http://localhost:5000/redoc

## Accessing the database

The application uses SQLite as the database, with the file located in the `data/` directory.
In the container, the database is mounted as a volume, so data is preserved between runs.

## API Endpoints

### Application Health

```
GET /health
```

Checks the status of the API and database connection.

### Authorization

```
POST /api/auth/register
POST /api/auth/login
```

Used for registering a new user and logging in.
