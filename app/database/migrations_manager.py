"""
Module for managing database migrations with Alembic.
"""

import os
import logging
from pathlib import Path
import time
import threading
from typing import Optional

from alembic.config import Config
from alembic import command

logger = logging.getLogger(__name__)

def get_alembic_config() -> Config:
    """
    Create and return a properly configured alembic Config object.
    
    Returns:
        Config: Configured alembic Config object
    """
    # Get the directory where this file is located
    base_dir = Path(__file__).resolve().parent
    
    # Alembic config is in the migrations folder
    alembic_cfg = Config(str(base_dir / "migrations" / "alembic.ini"))
    
    # Set the script_location to the migrations directory
    alembic_cfg.set_main_option("script_location", str(base_dir / "migrations"))
    
    # Set the sqlalchemy.url from environment if available
    data_dir = os.environ.get("DATA_DIRECTORY", "./data")
    db_path = os.path.join(data_dir, "todoist.db")
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    
    return alembic_cfg

def run_migrations() -> None:
    """
    Run database migrations using Alembic.
    
    This function runs all pending migrations to bring the database
    schema up to the latest version.
    
    Raises:
        Exception: If migrations fail
    """
    try:
        # Create data directory if it doesn't exist
        data_dir = os.environ.get("DATA_DIRECTORY", "./data")
        if not os.path.exists(data_dir):
            logger.info(f"Creating data directory: {data_dir}")
            os.makedirs(data_dir, exist_ok=True)
        
        logger.info("Running database migrations...")
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully.")
    except Exception as e:
        logger.error(f"Error running database migrations: {str(e)}")
        # Re-raise the exception to be handled by the caller
        raise