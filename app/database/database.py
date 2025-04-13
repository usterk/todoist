import os
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Get data directory path from environment variables or use default
DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY", "./data")
DATABASE_URL = f"sqlite:///{DATA_DIRECTORY}/todoist.db"

# Ensure data directory exists
os.makedirs(DATA_DIRECTORY, exist_ok=True)

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, Any, None]:
    """
    Create and yield a database session.
    
    This function provides a database session for dependency injection in FastAPI.
    The session is automatically closed when the request is complete.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()