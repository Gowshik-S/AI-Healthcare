"""
Pydantic schemas for request/response validation.
All responses follow the standard format with status, data, message, timestamp.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TriggerAction(str, Enum):
    ER = "ER"
    CLINIC = "Clinic"
    HOME = "Home"


# ==================== STANDARD RESPONSE ====================

class StandardResponse(BaseModel):
    """Standard API response format."""
    status: str = "success"
    data: Optional[Any] = None
    message: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== AUTH SCHEMAS ====================

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.PATIENT


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== PATIENT SCHEMAS ====================

class PatientBase(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    existing_conditions: Optional[str] = None


class PatientCreate(PatientBase):
    pass


class PatientUpdate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PatientFullResponse(PatientResponse):
    user: UserResponse


# ==================== DOCTOR SCHEMAS ====================

class DoctorBase(BaseModel):
    specialization: str
    license_number: str
    hospital_name: Optional[str] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    hospital_name: Optional[str] = None


class DoctorResponse(DoctorBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class DoctorFullResponse(DoctorResponse):
    user: UserResponse


# ==================== SYMPTOM SCHEMAS ====================

class SymptomBase(BaseModel):
    name: str
    description: Optional[str] = None
    severity: int = Field(..., ge=1, le=10)
    risk_level: RiskLevel = RiskLevel.LOW
    body_system: Optional[str] = None


class SymptomCreate(SymptomBase):
    pass


class SymptomResponse(SymptomBase):
    id: int

    class Config:
        from_attributes = True


# ==================== TRIAGE SCHEMAS ====================

class TriageStart(BaseModel):
    """Start a new triage session."""
    pass  # Patient ID comes from auth token


class TriageAddSymptom(BaseModel):
    """Add a symptom to an active triage session."""
    session_id: int
    symptom_id: int


class TriageSessionResponse(BaseModel):
    id: int
    patient_id: int
    symptoms_reported: Optional[List[int]] = []
    risk_score: Optional[float] = None
    triage_result: Optional[TriggerAction] = None
    ai_recommendation: Optional[str] = None
    status: str
    timestamp: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TriageResultResponse(TriageSessionResponse):
    symptoms_details: Optional[List[SymptomResponse]] = []
    recommended_action: Optional[str] = None


# ==================== CONSULTATION SCHEMAS ====================

class ConsultationBase(BaseModel):
    diagnosis: Optional[str] = None
    notes: Optional[str] = None


class ConsultationCreate(ConsultationBase):
    patient_id: int
    doctor_id: int


class ConsultationUpdate(ConsultationBase):
    pass


class ConsultationResponse(ConsultationBase):
    id: int
    patient_id: int
    doctor_id: int
    date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== PRESCRIPTION SCHEMAS ====================

class PrescriptionBase(BaseModel):
    drug_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    consultation_id: int


class PrescriptionResponse(PrescriptionBase):
    id: int
    consultation_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== RED FLAG SCHEMAS ====================

class RedFlagBase(BaseModel):
    name: str
    symptom_combination: List[int]
    trigger_action: TriggerAction
    description: Optional[str] = None
    priority: int = 1


class RedFlagCreate(RedFlagBase):
    pass


class RedFlagResponse(RedFlagBase):
    id: int

    class Config:
        from_attributes = True
