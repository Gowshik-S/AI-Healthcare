"""
Consultation and Prescription routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Patient, Doctor, Consultation, Prescription, UserRole
from schemas import ConsultationCreate, PrescriptionCreate
from utils import get_current_user, success_response, error_response

router = APIRouter(tags=["Consultations"])


# ==================== CONSULTATION ENDPOINTS ====================

@router.get("/consultations/all", response_model=dict)
async def get_all_consultations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all consultations for the current user.
    Returns different data based on role (patient sees their consultations, doctor sees their appointments).
    """
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found"
            )
        
        consultations = db.query(Consultation).filter(
            Consultation.patient_id == patient.id
        ).order_by(Consultation.date.desc()).all()
        
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found"
            )
        
        consultations = db.query(Consultation).filter(
            Consultation.doctor_id == doctor.id
        ).order_by(Consultation.date.desc()).all()
        
    else:  # Admin
        consultations = db.query(Consultation).order_by(
            Consultation.date.desc()
        ).limit(100).all()
    
    consultations_list = []
    for c in consultations:
        # Get related info
        patient = db.query(Patient).filter(Patient.id == c.patient_id).first()
        patient_user = db.query(User).filter(User.id == patient.user_id).first() if patient else None
        doctor = db.query(Doctor).filter(Doctor.id == c.doctor_id).first()
        doctor_user = db.query(User).filter(User.id == doctor.user_id).first() if doctor else None
        
        consultations_list.append({
            "id": c.id,
            "date": c.date.isoformat() if c.date else None,
            "diagnosis": c.diagnosis,
            "notes": c.notes,
            "patient": {
                "id": patient.id if patient else None,
                "name": patient_user.name if patient_user else "Unknown"
            },
            "doctor": {
                "id": doctor.id if doctor else None,
                "name": doctor_user.name if doctor_user else "Unknown",
                "specialization": doctor.specialization if doctor else None
            }
        })
    
    return success_response(
        data={
            "consultations": consultations_list,
            "total": len(consultations_list)
        },
        message="Consultations retrieved"
    )


@router.post("/consultations/create", response_model=dict)
async def create_consultation(
    consultation_data: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new consultation (doctor only).
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create consultations"
        )
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == consultation_data.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    consultation = Consultation(
        patient_id=consultation_data.patient_id,
        doctor_id=doctor.id,
        diagnosis=consultation_data.diagnosis,
        notes=consultation_data.notes
    )
    
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    return success_response(
        data={
            "id": consultation.id,
            "patient_id": consultation.patient_id,
            "doctor_id": consultation.doctor_id,
            "date": consultation.date.isoformat() if consultation.date else None,
            "diagnosis": consultation.diagnosis
        },
        message="Consultation created successfully"
    )


@router.get("/consultations/{consultation_id}", response_model=dict)
async def get_consultation_details(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific consultation.
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    # Verify access
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or consultation.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or consultation.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Get prescriptions
    prescriptions = db.query(Prescription).filter(
        Prescription.consultation_id == consultation_id
    ).all()
    
    # Get related entities
    patient = db.query(Patient).filter(Patient.id == consultation.patient_id).first()
    patient_user = db.query(User).filter(User.id == patient.user_id).first() if patient else None
    doctor = db.query(Doctor).filter(Doctor.id == consultation.doctor_id).first()
    doctor_user = db.query(User).filter(User.id == doctor.user_id).first() if doctor else None
    
    return success_response(
        data={
            "id": consultation.id,
            "date": consultation.date.isoformat() if consultation.date else None,
            "diagnosis": consultation.diagnosis,
            "notes": consultation.notes,
            "patient": {
                "id": patient.id if patient else None,
                "name": patient_user.name if patient_user else "Unknown",
                "age": patient.age if patient else None,
                "gender": patient.gender if patient else None
            },
            "doctor": {
                "id": doctor.id if doctor else None,
                "name": doctor_user.name if doctor_user else "Unknown",
                "specialization": doctor.specialization if doctor else None,
                "hospital": doctor.hospital_name if doctor else None
            },
            "prescriptions": [
                {
                    "id": p.id,
                    "drug_name": p.drug_name,
                    "dosage": p.dosage,
                    "frequency": p.frequency,
                    "duration": p.duration,
                    "instructions": p.instructions
                }
                for p in prescriptions
            ]
        },
        message="Consultation details retrieved"
    )


# ==================== PRESCRIPTION ENDPOINTS ====================

@router.post("/prescriptions/add", response_model=dict)
async def add_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a prescription to a consultation (doctor only).
    """
    if current_user.role != UserRole.DOCTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can add prescriptions"
        )
    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Verify consultation exists and belongs to this doctor
    consultation = db.query(Consultation).filter(
        Consultation.id == prescription_data.consultation_id
    ).first()
    
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    if consultation.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only add prescriptions to your own consultations"
        )
    
    prescription = Prescription(
        consultation_id=prescription_data.consultation_id,
        drug_name=prescription_data.drug_name,
        dosage=prescription_data.dosage,
        frequency=prescription_data.frequency,
        duration=prescription_data.duration,
        instructions=prescription_data.instructions
    )
    
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    
    return success_response(
        data={
            "id": prescription.id,
            "consultation_id": prescription.consultation_id,
            "drug_name": prescription.drug_name,
            "dosage": prescription.dosage,
            "frequency": prescription.frequency,
            "duration": prescription.duration,
            "instructions": prescription.instructions
        },
        message="Prescription added successfully"
    )


@router.get("/prescriptions/{consultation_id}", response_model=dict)
async def get_prescriptions(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all prescriptions for a consultation.
    """
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    # Verify access
    if current_user.role == UserRole.PATIENT:
        patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
        if not patient or consultation.patient_id != patient.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif current_user.role == UserRole.DOCTOR:
        doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
        if not doctor or consultation.doctor_id != doctor.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    prescriptions = db.query(Prescription).filter(
        Prescription.consultation_id == consultation_id
    ).all()
    
    return success_response(
        data={
            "consultation_id": consultation_id,
            "prescriptions": [
                {
                    "id": p.id,
                    "drug_name": p.drug_name,
                    "dosage": p.dosage,
                    "frequency": p.frequency,
                    "duration": p.duration,
                    "instructions": p.instructions,
                    "created_at": p.created_at.isoformat() if p.created_at else None
                }
                for p in prescriptions
            ],
            "total": len(prescriptions)
        },
        message="Prescriptions retrieved"
    )
