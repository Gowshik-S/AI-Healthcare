"""
Database configuration and session management for Healthcare Triage System.
Uses SQLite for offline-first capability.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite database URL - stored locally for offline support
SQLALCHEMY_DATABASE_URL = "sqlite:///./healthcare_triage.db"

# Create engine with check_same_thread=False for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
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
