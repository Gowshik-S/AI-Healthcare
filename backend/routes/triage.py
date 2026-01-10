"""
Triage routes - Symptom assessment and risk scoring.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from database import get_db
from models import User, Patient, Symptom, TriageSession, RedFlag, UserRole, TriggerAction
from schemas import TriageStart, TriageAddSymptom, SymptomCreate
from utils import get_current_user, success_response, error_response

router = APIRouter(prefix="/triage", tags=["Triage"])


def calculate_risk_score(symptoms: List[Symptom], red_flags: List[RedFlag]) -> tuple:
    """
    Calculate risk score based on symptoms and check for red flags.
    
    Returns:
        Tuple of (risk_score, triage_result, matched_red_flags)
    """
    if not symptoms:
        return 0.0, TriggerAction.HOME, []
    
    # Calculate base score from symptom severities
    total_severity = sum(s.severity for s in symptoms)
    avg_severity = total_severity / len(symptoms)
    
    # Weight by risk levels
    risk_weights = {"low": 1, "medium": 2, "high": 3, "critical": 5}
    weighted_score = sum(
        s.severity * risk_weights.get(s.risk_level.value, 1)
        for s in symptoms
    ) / len(symptoms)
    
    # Normalize to 0-100 scale
    risk_score = min(100, (weighted_score / 50) * 100)
    
    # Check for red flag combinations
    symptom_ids = set(s.id for s in symptoms)
    matched_red_flags = []
    
    for rf in red_flags:
        rf_symptoms = set(rf.symptom_combination) if rf.symptom_combination else set()
        if rf_symptoms.issubset(symptom_ids):
            matched_red_flags.append(rf)
    
    # Determine triage result
    if matched_red_flags:
        # Use highest priority red flag
        highest_priority = max(matched_red_flags, key=lambda x: x.priority)
        triage_result = highest_priority.trigger_action
    elif risk_score >= 70:
        triage_result = TriggerAction.ER
    elif risk_score >= 40:
        triage_result = TriggerAction.CLINIC
    else:
        triage_result = TriggerAction.HOME
    
    return risk_score, triage_result, matched_red_flags


@router.post("/start", response_model=dict)
async def start_triage_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a new triage session for the current patient.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can start triage sessions"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Check for existing active session
    active_session = db.query(TriageSession).filter(
        TriageSession.patient_id == patient.id,
        TriageSession.status == "in_progress"
    ).first()
    
    if active_session:
        return success_response(
            data={
                "session_id": active_session.id,
                "status": active_session.status,
                "symptoms_reported": active_session.symptoms_reported or [],
                "message": "Continuing existing session"
            },
            message="Active triage session found"
        )
    
    # Create new session
    new_session = TriageSession(
        patient_id=patient.id,
        symptoms_reported=[],
        status="in_progress"
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return success_response(
        data={
            "session_id": new_session.id,
            "status": new_session.status,
            "symptoms_reported": [],
            "timestamp": new_session.timestamp.isoformat()
        },
        message="Triage session started"
    )


@router.post("/add-symptom", response_model=dict)
async def add_symptom_to_session(
    symptom_data: TriageAddSymptom,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a symptom to an active triage session.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can add symptoms"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    # Get session
    session = db.query(TriageSession).filter(
        TriageSession.id == symptom_data.session_id,
        TriageSession.patient_id == patient.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage session not found"
        )
    
    if session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add symptoms to a completed session"
        )
    
    # Verify symptom exists
    symptom = db.query(Symptom).filter(Symptom.id == symptom_data.symptom_id).first()
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    
    # Add symptom to session
    current_symptoms = session.symptoms_reported or []
    if symptom_data.symptom_id not in current_symptoms:
        current_symptoms.append(symptom_data.symptom_id)
        session.symptoms_reported = current_symptoms
        db.commit()
        db.refresh(session)
    
    return success_response(
        data={
            "session_id": session.id,
            "symptoms_reported": session.symptoms_reported,
            "symptom_added": {
                "id": symptom.id,
                "name": symptom.name,
                "severity": symptom.severity,
                "risk_level": symptom.risk_level.value
            }
        },
        message="Symptom added to session"
    )


@router.get("/result/{session_id}", response_model=dict)
async def get_triage_result(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the triage result for a session.
    Calculates risk score and determines recommended action.
    """
    if current_user.role != UserRole.PATIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view triage results"
        )
    
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    session = db.query(TriageSession).filter(
        TriageSession.id == session_id,
        TriageSession.patient_id == patient.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Triage session not found"
        )
    
    # Get symptoms
    symptom_ids = session.symptoms_reported or []
    symptoms = db.query(Symptom).filter(Symptom.id.in_(symptom_ids)).all() if symptom_ids else []
    
    # Get red flags
    red_flags = db.query(RedFlag).all()
    
    # Calculate risk
    risk_score, triage_result, matched_red_flags = calculate_risk_score(symptoms, red_flags)
    
    # Update session
    session.risk_score = risk_score
    session.triage_result = triage_result
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(session)
    
    # Prepare recommendation text
    recommendations = {
        TriggerAction.ER: "Seek emergency medical attention immediately. Go to the nearest emergency room.",
        TriggerAction.CLINIC: "Schedule an appointment with a healthcare provider within 24-48 hours.",
        TriggerAction.HOME: "Monitor your symptoms at home. Rest and stay hydrated. Seek care if symptoms worsen."
    }
    
    return success_response(
        data={
            "session_id": session.id,
            "risk_score": round(risk_score, 2),
            "triage_result": triage_result.value,
            "recommendation": recommendations.get(triage_result, ""),
            "symptoms_analyzed": [
                {
                    "id": s.id,
                    "name": s.name,
                    "severity": s.severity,
                    "risk_level": s.risk_level.value
                }
                for s in symptoms
            ],
            "red_flags_triggered": [
                {
                    "name": rf.name,
                    "action": rf.trigger_action.value
                }
                for rf in matched_red_flags
            ],
            "completed_at": session.completed_at.isoformat()
        },
        message="Triage assessment completed"
    )


@router.get("/symptoms", response_model=dict)
async def list_symptoms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of all available symptoms for selection.
    """
    symptoms = db.query(Symptom).order_by(Symptom.name).all()
    
    return success_response(
        data={
            "symptoms": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "severity": s.severity,
                    "risk_level": s.risk_level.value,
                    "body_system": s.body_system
                }
                for s in symptoms
            ],
            "total": len(symptoms)
        },
        message="Symptoms retrieved"
    )


@router.post("/symptoms", response_model=dict)
async def create_symptom(
    symptom_data: SymptomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new symptom (admin only).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create symptoms"
        )
    
    # Check if symptom already exists
    existing = db.query(Symptom).filter(Symptom.name == symptom_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Symptom with this name already exists"
        )
    
    from models import RiskLevel as ModelRiskLevel
    
    symptom = Symptom(
        name=symptom_data.name,
        description=symptom_data.description,
        severity=symptom_data.severity,
        risk_level=ModelRiskLevel(symptom_data.risk_level.value),
        body_system=symptom_data.body_system
    )
    
    db.add(symptom)
    db.commit()
    db.refresh(symptom)
    
    return success_response(
        data={
            "id": symptom.id,
            "name": symptom.name,
            "severity": symptom.severity,
            "risk_level": symptom.risk_level.value
        },
        message="Symptom created successfully"
    )
