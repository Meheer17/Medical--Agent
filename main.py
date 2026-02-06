from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from config import settings
from database import init_db, get_db
from models import User
from routes_auth import router as auth_router
from dependencies import get_current_active_user
from schemas import UserResponse

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Nithin App API",
    description="FastAPI backend with JWT authentication and MySQL database",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint to verify API is running"""
    return {
        "status": "healthy",
        "message": "API is running successfully"
    }

# Get current user info endpoint
@app.get(
    "/api/users/me",
    response_model=UserResponse,
    tags=["users"]
)
async def get_me(
    current_user: User = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return current_user

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Nithin App API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
