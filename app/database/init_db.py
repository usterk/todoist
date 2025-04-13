import os
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database.database import engine, Base
from app.models.user import User
from app.database.migrations_manager import run_migrations

# Password encryption context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
        admin_user = db.query(User).filter(User.username == "admin").first()
        
        if not admin_user:
            # Create default admin user
            hashed_password = pwd_context.hash("admin")
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=hashed_password
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created")
        else:
            print("Admin user already exists")
    except Exception as e:
        db.rollback()
        print(f"Error during database initialization: {e}")
    finally:
        db.close()