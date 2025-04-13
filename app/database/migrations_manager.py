"""
Module for managing database migrations with Alembic.
"""

import os
import logging
from pathlib import Path
from alembic.config import Config
from alembic import command

logger = logging.getLogger(__name__)

def get_alembic_config() -> Config:
    """
    Get Alembic configuration from the migrations directory.
    
    Returns:
        Config: Alembic configuration object
    """
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    alembic_cfg = Config(os.path.join(migrations_dir, "alembic.ini"))
    return alembic_cfg


def run_migrations() -> None:
    """
    Run database migrations to latest version.
    """
    try:
        # Ensure data directory exists
        data_dir = os.environ.get("DATA_DIRECTORY", "./data")
        Path(data_dir).mkdir(exist_ok=True)
        
        # Get Alembic config
        alembic_cfg = get_alembic_config()
        
        # Run migrations
        logger.info("Running database migrations...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")
    except Exception as e:
        logger.error(f"Error running database migrations: {e}")
        raise