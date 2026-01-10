"""
SQLAlchemy models for Healthcare Triage System.
Defines all database tables and relationships.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, 
    ForeignKey, Enum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class UserRole(str, enum.Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TriggerAction(str, enum.Enum):
    ER = "ER"
    CLINIC = "Clinic"
    HOME = "Home"


class User(Base):
    """Base user table for authentication and role management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient_profile = relationship("Patient", back_populates="user", uselist=False)
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)


class Patient(Base):
    """Patient-specific information linked to user."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    blood_group = Column(String(10), nullable=True)
    allergies = Column(Text, nullable=True)  # JSON string of allergies
    existing_conditions = Column(Text, nullable=True)  # JSON string of conditions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="patient_profile")
    consultations = relationship("Consultation", back_populates="patient")
    triage_sessions = relationship("TriageSession", back_populates="patient")


class Doctor(Base):
    """Doctor-specific information linked to user."""
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    specialization = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    hospital_name = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    consultations = relationship("Consultation", back_populates="doctor")


class Consultation(Base):
    """Medical consultations between doctors and patients."""
    __tablename__ = "consultations"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    diagnosis = Column(Text, nullable=True)
    prescription = Column(Text, nullable=True)  # Legacy field, use prescriptions table
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("Doctor", back_populates="consultations")
    prescriptions = relationship("Prescription", back_populates="consultation")


class Symptom(Base):
    """Master list of symptoms with severity and risk levels."""
    __tablename__ = "symptoms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Integer, nullable=False)  # 1-10 scale
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.LOW)
    body_system = Column(String(50), nullable=True)  # e.g., "respiratory", "cardiac"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TriageSession(Base):
    """Triage sessions for patient symptom assessment."""
    __tablename__ = "triage_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    symptoms_reported = Column(JSON, nullable=True)  # List of symptom IDs
    risk_score = Column(Float, nullable=True)  # Calculated risk score
    triage_result = Column(Enum(TriggerAction), nullable=True)
    ai_recommendation = Column(Text, nullable=True)  # For Phase 3 AI integration
    status = Column(String(20), default="in_progress")  # in_progress, completed
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="triage_sessions")


class Prescription(Base):
    """Detailed prescription records for consultations."""
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False)
    drug_name = Column(String(100), nullable=False)
    dosage = Column(String(50), nullable=False)  # e.g., "500mg"
    frequency = Column(String(50), nullable=False)  # e.g., "twice daily"
    duration = Column(String(50), nullable=False)  # e.g., "7 days"
    instructions = Column(Text, nullable=True)  # Special instructions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="prescriptions")


class RedFlag(Base):
    """Red flag symptom combinations that require immediate action."""
    __tablename__ = "red_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    symptom_combination = Column(JSON, nullable=False)  # List of symptom IDs
    trigger_action = Column(Enum(TriggerAction), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=1)  # Higher = more urgent
    created_at = Column(DateTime(timezone=True), server_default=func.now())
