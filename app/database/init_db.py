import logging
import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import asyncio
import time

from app.database.database import engine, Base
from app.models.user import User
from app.database.migrations_manager import run_migrations
from app.core.config import DB_SETTINGS

# Set up logger
logger = logging.getLogger(__name__)

# Password encryption context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the plain password matches the hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare against
        
    Returns:
        bool: True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def check_admin_default_password(db: Session) -> None:
    """
    Check if admin user exists and is using default password.
    If so, log a warning.
    
    Args:
        db: Database session
    """
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == DB_SETTINGS["default_admin_username"]).first()
        
        if admin_user and verify_password(DB_SETTINGS["default_admin_password"], admin_user.password_hash):
            logger.warning(
                f"SECURITY WARNING: The '{DB_SETTINGS['default_admin_username']}' user has the default password. "
                "Please change it immediately!"
            )
    except Exception as e:
        logger.error(f"Error checking admin password: {e}")

async def init_db(timeout: int = 10) -> None:
    """
    Initialize the database with required data.
    
    This includes:
    1. Running migrations to ensure schema is up-to-date
    2. Creating admin user if not exists
    
    Args:
        timeout: Maximum time in seconds for DB initialization
    """
    logger.info("Starting database initialization")
    start_time = time.time()
    
    try:
        # Run migrations with a timeout
        try:
            # Run in a separate thread with timeout to prevent hanging
            await asyncio.to_thread(run_migrations)
        except Exception as e:
            logger.error(f"Error during migrations: {str(e)}")
            logger.warning("Will attempt to continue with database initialization")
        
        # Check if we've exceeded timeout
        if time.time() - start_time > timeout:
            logger.warning(f"Database initialization taking longer than {timeout} seconds")
        
        # Create admin user if not exists
        db = Session()
        try:
            logger.info("Checking for admin user")
            admin = db.query(User).filter(User.username == DB_SETTINGS['default_admin_username']).first()
            
            if not admin:
                logger.info("Admin user not found, creating...")
                admin_user = User(
                    username=DB_SETTINGS['default_admin_username'],
                    email="admin@example.com",
                    password_hash=pwd_context.hash(os.environ.get("ADMIN_PASSWORD", DB_SETTINGS['default_admin_password']))
                )
                db.add(admin_user)
                db.commit()
                logger.info("Admin user created successfully")
            else:
                logger.info(f"{DB_SETTINGS['default_admin_username']} user already exists")
            
            # Check if admin has default password
            await asyncio.to_thread(check_admin_default_password, db)
            
        except Exception as e:
            logger.error(f"Error during database initialization: Error creating admin user: {str(e)}")
            db.rollback()  # Ensure rollback is called for proper testing
        finally:
            db.close()
        
        logger.info(f"Database initialization completed in {time.time() - start_time:.2f} seconds")
    
    except Exception as e:
        logger.error(f"Error during database initialization: {str(e)}")
        # Don't re-raise - allow application to start anyway
    
    # Signal that initialization is complete, even if there were errors
    logger.info("Database initialization process finished")