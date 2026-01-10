"""
Routes package for Healthcare Triage API.
"""
from .auth import router as auth_router
from .patients import router as patients_router
from .doctors import router as doctors_router
from .triage import router as triage_router
from .consultations import router as consultations_router

__all__ = [
    "auth_router",
    "patients_router", 
    "doctors_router",
    "triage_router",
    "consultations_router"
]
