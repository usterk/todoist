"""
Health check endpoint to verify API availability.
"""

import logging
import os
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database.database import get_db, DATABASE_URL

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
    - Database diagnostics (when connection fails)
    
    Returns:
        Dict[str, Any]: Health check response data
    """
    logger.info("Health check requested")
    
    # Check if database is connected
    db_status = {}
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            db_connected = "connected"
        else:
            db_connected = "disconnected"
            db_status["query_result"] = str(result)
    except SQLAlchemyError as e:
        logger.error(f"Database health check query failed: {str(e)}")
        db_connected = "disconnected"
        db_status["error"] = str(e)
    except Exception as e:
        logger.error(f"Database health check failed with unexpected error: {str(e)}")
        db_connected = "disconnected"
        db_status["error"] = str(e)
    
    # Add database file check
    db_path = DATABASE_URL.replace("sqlite:///", "")
    db_status["file_exists"] = os.path.exists(db_path)
    db_status["file_path"] = db_path
    
    # Return health status
    response = {
        "status": "ok",
        "api_version": "1.0.0",
        "database": db_connected,
    }
    
    # Add diagnostics if database is disconnected
    if db_connected == "disconnected":
        response["database_diagnostics"] = db_status
    
    return response