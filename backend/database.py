"""
Database configuration and session management for Healthcare Triage System.
Supports PostgreSQL (production) and SQLite (development).
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import settings

# Get database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create engine with appropriate settings based on database type
if settings.is_sqlite:
    # SQLite configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration with SSL support (for Neon, Supabase, etc.)
    connect_args = {}
    
    # Check if SSL is required (common for cloud providers like Neon)
    if "sslmode=require" in SQLALCHEMY_DATABASE_URL:
        connect_args["sslmode"] = "require"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Enable connection health checks
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_recycle=300,  # Recycle connections after 5 minutes
        connect_args=connect_args if connect_args else {}
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session.
    Ensures proper cleanup after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Called on application startup.
    """
    from models import (
        User, Patient, Doctor, Consultation, 
        Symptom, TriageSession, Prescription, RedFlag
    )
    Base.metadata.create_all(bind=engine)
    
    db_type = "PostgreSQL (Neon)" if "neon.tech" in SQLALCHEMY_DATABASE_URL else "PostgreSQL" if settings.is_postgresql else "SQLite"
    print(f"📦 Database: {db_type}")
    print(f"   Pool Size: {settings.DB_POOL_SIZE}, Max Overflow: {settings.DB_MAX_OVERFLOW}")
