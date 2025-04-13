from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.database.init_db import init_db

app = FastAPI(
    title="Todoist API",
    description="Task Management API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    await init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)