"""
Healthcare Triage System - FastAPI Application
Main entry point for the backend API.
"""
import logging
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

# Configure logging based on environment
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes database on startup.
    """
    # Startup
    logger.info("🏥 Healthcare Triage System Starting...")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 CORS Origins: {settings.CORS_ORIGINS}")
    init_db()
    logger.info("✅ Database initialized")
    yield
    # Shutdown
    logger.info("👋 Healthcare Triage System Shutting down...")


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
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG or not settings.is_production else None,
    redoc_url="/redoc" if settings.DEBUG or not settings.is_production else None,
)

# Configure CORS - use specific origins from environment
# In development, allow all origins for easier testing
if settings.is_production and settings.CORS_ORIGINS:
    cors_origins = settings.CORS_ORIGINS
else:
    cors_origins = ["*"]

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
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if not settings.is_production else "disabled"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check.
    """
    return {
        "status": "healthy",
        "database": "PostgreSQL" if settings.is_postgresql else "SQLite",
        "environment": settings.ENVIRONMENT,
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG
    )
