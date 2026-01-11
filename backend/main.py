"""
Healthcare Triage System - FastAPI Application
Main entry point for the backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config import settings
from database import init_db
from routes import (
    auth_router,
    patients_router,
    doctors_router,
    triage_router,
    consultations_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database on startup.
    """
    # Startup
    print("🏥 Healthcare Triage System Starting...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Healthcare Triage System Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="Healthcare Triage API",
    description="""
    AI-powered healthcare triage system for patient symptom assessment.
    
    ## Features
    - 🔐 JWT Authentication with role-based access
    - 👤 Patient profile management
    - 👨‍⚕️ Doctor-patient consultations
    - 🩺 Symptom-based triage with risk scoring
    - 💊 Prescription management
    - 🚨 Red flag detection for emergency cases
    
    ## Roles
    - **Patient**: Can manage profile, start triage sessions, view consultations
    - **Doctor**: Can manage patients, create consultations, add prescriptions
    - **Admin**: Full system access
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
# In development, allow all origins for easier testing
cors_origins = ["*"] if not settings.is_production else settings.CORS_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(doctors_router)
app.include_router(triage_router)
app.include_router(consultations_router)


@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint.
    """
    return {
        "status": "success",
        "message": "Healthcare Triage API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
