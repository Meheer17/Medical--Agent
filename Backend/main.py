from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from config import settings
from database import init_db, get_db, close_mongo_connection
from routes_auth import router as auth_router
from routes_appointments import router as appointments_router
from routes_reports import router as reports_router
from routes_profiles import router as profiles_router
from routes_queries import router as queries_router
from dependencies import get_current_active_user, DictWrapper
from schemas import UserResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MongoDB connection and indexes on startup
    await init_db()
    yield
    await close_mongo_connection()

# Create FastAPI app
app = FastAPI(
    title="ClinIQ API",
    description="FastAPI backend with JWT authentication and MongoDB database",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(appointments_router)
app.include_router(reports_router)
app.include_router(profiles_router)
app.include_router(queries_router)

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
    current_user: DictWrapper = Depends(get_current_active_user)
):
    """Get current authenticated user information"""
    return current_user

# File download endpoint
@app.get(
    "/api/file/{report_id}",
    tags=["files"]
)
async def download_file(
    report_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """
    Download a lab report PDF file
    
    Only authorized users (patient, assigned doctor, or lab) can download
    """
    report = await db.lab_reports.find_one({"id": report_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    appointment = await db.lab_appointments.find_one({"id": report["appointment_id"]})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated appointment not found"
        )
    
    is_patient = current_user.id == appointment["patient_id"]
    is_doctor = current_user.id == appointment["doctor_id"] if appointment.get("doctor_id") else False
    is_lab = current_user.id == appointment["lab_id"]
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this file"
        )
    
    return FileResponse(
        path=report["file_path"],
        filename=report["file_name"],
        media_type=report.get("mime_type", "application/pdf")
    )

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to ClinIQ API",
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
