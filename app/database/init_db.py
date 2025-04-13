import logging
import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session

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

async def init_db() -> None:
    """
    Initialize the database by running migrations and creating default admin user if needed.
    """
    # Run database migrations to create/update schema
    run_migrations()
    
    # Create admin user if not exists
    db = Session(engine)
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == DB_SETTINGS["default_admin_username"]).first()
        
        if not admin_user:
            # Create default admin user
            hashed_password = pwd_context.hash(DB_SETTINGS["default_admin_password"])
            admin_user = User(
                username=DB_SETTINGS["default_admin_username"],
                email=DB_SETTINGS["default_admin_email"],
                password_hash=hashed_password
            )
            db.add(admin_user)
            db.commit()
            logger.info(f"Default {DB_SETTINGS['default_admin_username']} user created")
        else:
            logger.info(f"{DB_SETTINGS['default_admin_username']} user already exists")
            
        # Check if admin has default password and warn if needed
        check_admin_default_password(db)
    except Exception as e:
        db.rollback()
        logger.error(f"Error during database initialization: {e}")
    finally:
        db.close()