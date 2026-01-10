"""
Patient routes - Profile management for patients.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Patient, UserRole
from schemas import PatientUpdate, PatientResponse
from utils import get_current_user, get_current_patient, success_response, error_response

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/profile", response_model=dict)
async def get_patient_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current patient's profile.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this endpoint"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    return success_response(
        data={
            "id": patient.id,
            "user_id": patient.user_id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "age": patient.age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "allergies": patient.allergies,
            "existing_conditions": patient.existing_conditions
        },
        message="Patient profile retrieved"
    )


@router.put("/profile", response_model=dict)
async def update_patient_profile(
    profile_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the current patient's profile.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this endpoint"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Update fields if provided
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return success_response(
        data={
            "id": patient.id,
            "user_id": patient.user_id,
            "age": patient.age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "allergies": patient.allergies,
            "existing_conditions": patient.existing_conditions
        },
        message="Patient profile updated successfully"
    )


@router.get("/history", response_model=dict)
async def get_patient_medical_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get patient's medical history including consultations and triage sessions.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can access this endpoint"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Get consultations
    consultations = [
        {
            "id": c.id,
            "doctor_id": c.doctor_id,
            "date": c.date.isoformat() if c.date else None,
            "diagnosis": c.diagnosis,
            "notes": c.notes
        }
        for c in patient.consultations
    ]
    
    # Get triage sessions
    triage_sessions = [
        {
            "id": t.id,
            "symptoms_reported": t.symptoms_reported,
            "risk_score": t.risk_score,
            "triage_result": t.triage_result.value if t.triage_result else None,
            "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            "status": t.status
        }
        for t in patient.triage_sessions
    ]
    
    return success_response(
        data={
            "patient_id": patient.id,
            "consultations": consultations,
            "triage_sessions": triage_sessions
        },
        message="Medical history retrieved"
    )
