"""
Health check endpoint to verify API availability.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> dict:
    """
    Health check endpoint to verify API and database availability.
    
    Args:
        db: Database session dependency
        
    Returns:
        dict: Status message and version information
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "api_version": "1.0.0",
        "database": db_status
    }