"""
Authentication routes - User registration and login.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User, Patient, Doctor, UserRole
from schemas import UserCreate, UserLogin, UserResponse, TokenResponse, StandardResponse
from utils import (
    hash_password, verify_password, create_access_token,
    success_response, error_response
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Creates user account and associated patient/doctor profile based on role.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        phone=user_data.phone
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create associated profile based on role
    if user_data.role == UserRole.PATIENT:
        patient_profile = Patient(user_id=new_user.id)
        db.add(patient_profile)
        db.commit()
    elif user_data.role == UserRole.DOCTOR:
        # Doctor profile needs additional info - create placeholder
        # Will need to be updated with specialization and license
        pass
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.id})
    
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role.value,
                "phone": new_user.phone
            }
        },
        message="Registration successful"
    )


@router.post("/login", response_model=dict)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate token
    access_token = create_access_token(data={"sub": user.id})
    
    return success_response(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value,
                "phone": user.phone
            }
        },
        message="Login successful"
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(__import__('utils', fromlist=['get_current_user']).get_current_user)
):
    """
    Get current authenticated user's information.
    """
    return success_response(
        data={
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role.value,
            "phone": current_user.phone
        },
        message="User info retrieved"
    )
