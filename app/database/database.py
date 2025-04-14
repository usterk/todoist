import os
import time
import logging
from typing import Any, Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Set up logger
logger = logging.getLogger(__name__)

# Get data directory path from environment variables or use default
DATA_DIRECTORY = os.environ.get("DATA_DIRECTORY", "./data")
DATABASE_URL = f"sqlite:///{DATA_DIRECTORY}/todoist.db"

# Ensure data directory exists
os.makedirs(DATA_DIRECTORY, exist_ok=True)

# Create engine with retry mechanism
def create_db_engine(max_retries=3, retry_delay=2):
    """
    Create database engine with connection retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between attempts
        
    Returns:
        SQLAlchemy engine instance
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Create engine
            engine = create_engine(
                DATABASE_URL, connect_args={"check_same_thread": False}
            )
            
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1")).fetchone()
            
            logger.info(f"Database connection established successfully (attempt {attempt})")
            return engine
        
        except SQLAlchemyError as e:
            if attempt < max_retries:
                logger.warning(f"Database connection attempt {attempt} failed: {str(e)}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to establish database connection after {max_retries} attempts")
                # Create engine anyway - application can handle connection issues later
                return create_engine(
                    DATABASE_URL, connect_args={"check_same_thread": False}
                )

# Create engine with retry mechanism
engine = create_db_engine()
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