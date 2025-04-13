"""
Health check endpoint to verify API availability.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

# Set up logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Health check endpoint to verify API and database availability.
    
    This endpoint returns:
    - API status
    - API version
    - Database connection status
    
    Returns:
        Dict[str, Any]: Health check response data
    """
    logger.info("Health check requested")
    
    # Check if database is connected
    try:
        db.execute("SELECT 1").fetchone()
        db_connected = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_connected = "disconnected"
    
    # Return health status
    return {
        "status": "ok",
        "api_version": "1.0.0",
        "database": db_connected
    }