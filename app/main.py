import logging
import asyncio
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.protected import router as protected_router
from app.api.users import router as users_router
from app.api.projects import router as projects_router
from app.database.init_db import init_db
from app.models.user import User
from app.auth.auth import get_current_user
from app.schemas.user import UserResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Flag to track if initialization is complete
init_complete = False
init_error = None

app = FastAPI(
    title="Todoist API",
    description="Task management API",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(protected_router, prefix="/api", tags=["protected"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(projects_router)

@app.on_event("startup")
async def startup_db_client():
    global init_complete, init_error
    
    # Run database initialization in a background task to prevent blocking
    logger.info("Starting application initialization in background task...")
    
    async def init_db_background():
        global init_complete, init_error
        try:
            await init_db(timeout=15)
            init_complete = True
        except Exception as e:
            logger.error(f"Error during background initialization: {str(e)}")
            init_error = str(e)
            init_complete = True  # Mark as complete even if there's an error
    
    # Start background task but don't await it
    asyncio.create_task(init_db_background())
    logger.info("Application startup continues while initialization runs in background")

# Create a simple pre-startup health route that doesn't depend on DB
@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint for quick healthcheck that doesn't require database access.
    
    Returns:
        Dict[str, Any]: Simple status message
    """
    status_info = {
        "message": "Todoist API is running",
        "status": "initializing" if not init_complete else "ready",
        "version": app.version
    }
    
    if init_error:
        status_info["warning"] = "Application started with initialization errors"
        status_info["error"] = init_error
    
    return status_info

# Running the app directly
if __name__ == "__main__":
    logger.info("Starting Todoist API...")
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",  # Bind to all interfaces
        port=5000, 
        log_level="info",
        reload=False     # Disable reload in Docker
    )