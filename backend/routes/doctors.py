"""
Doctor routes - Patient management for doctors.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Doctor, Patient, Consultation, UserRole
from schemas import DoctorCreate, DoctorUpdate
from utils import get_current_user, get_current_doctor, success_response, error_response

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/profile", response_model=dict)
async def create_doctor_profile(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create or complete doctor profile.
    Required for doctors after registration.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )
    
    # Check if profile already exists
    existing = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor profile already exists"
        )
    
    # Check license number uniqueness
    license_exists = db.query(Doctor).filter(
        Doctor.license_number == doctor_data.license_number
    ).first()
    if license_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already registered"
        )
    
    doctor = Doctor(
        user_id=current_user.id,
        specialization=doctor_data.specialization,
        license_number=doctor_data.license_number,
        hospital_name=doctor_data.hospital_name
    )
    
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    
    return success_response(
        data={
            "id": doctor.id,
            "user_id": doctor.user_id,
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "hospital_name": doctor.hospital_name
        },
        message="Doctor profile created successfully"
    )


@router.get("/profile", response_model=dict)
async def get_doctor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the current doctor's profile.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found. Please complete your profile."
        )
    
    return success_response(
        data={
            "id": doctor.id,
            "user_id": doctor.user_id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "specialization": doctor.specialization,
            "license_number": doctor.license_number,
            "hospital_name": doctor.hospital_name
        },
        message="Doctor profile retrieved"
    )


@router.get("/patients", response_model=dict)
async def get_doctor_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all patients the doctor has consulted with.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get unique patients from consultations
    consultations = db.query(Consultation).filter(
        Consultation.doctor_id == doctor.id
    ).all()
    
    patient_ids = list(set(c.patient_id for c in consultations))
    patients = db.query(Patient).filter(Patient.id.in_(patient_ids)).all()
    
    patients_list = []
    for patient in patients:
        user = db.query(User).filter(User.id == patient.user_id).first()
        patient_consultations = [c for c in consultations if c.patient_id == patient.id]
        
        patients_list.append({
            "id": patient.id,
            "name": user.name if user else "Unknown",
            "email": user.email if user else None,
            "age": patient.age,
            "gender": patient.gender,
            "blood_group": patient.blood_group,
            "consultation_count": len(patient_consultations),
            "last_consultation": max(
                (c.date for c in patient_consultations),
                default=None
            ).isoformat() if patient_consultations and patient_consultations[0].date else None
        })
    
    return success_response(
        data={
            "doctor_id": doctor.id,
            "patient_count": len(patients_list),
            "patients": patients_list
        },
        message="Patients retrieved successfully"
    )


@router.get("/patients/{patient_id}", response_model=dict)
async def get_patient_details(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific patient.
    Only accessible if doctor has consulted with this patient.
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can access this endpoint"
        )
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Verify doctor has consulted with this patient
    consultation_exists = db.query(Consultation).filter(
        Consultation.doctor_id == doctor.id,
        Consultation.patient_id == patient_id
    ).first()
    
    if not consultation_exists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this patient's records"
        )
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    user = db.query(User).filter(User.id == patient.user_id).first()
    
    # Get all consultations with this patient
    consultations = db.query(Consultation).filter(
        Consultation.doctor_id == doctor.id,
        Consultation.patient_id == patient_id
    ).order_by(Consultation.date.desc()).all()
    
    return success_response(
        data={
            "patient": {
                "id": patient.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "age": patient.age,
                "gender": patient.gender,
                "blood_group": patient.blood_group,
                "allergies": patient.allergies,
                "existing_conditions": patient.existing_conditions
            },
            "consultations": [
                {
                    "id": c.id,
                    "date": c.date.isoformat() if c.date else None,
                    "diagnosis": c.diagnosis,
                    "notes": c.notes
                }
                for c in consultations
            ]
        },
        message="Patient details retrieved"
    )
