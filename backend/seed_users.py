"""
Seed script to create default test users for the Healthcare Triage System.
Run this script to populate the database with admin, doctor, and patient accounts.

Usage:
    python seed_users.py
"""
from database import SessionLocal, init_db
from models import User, Patient, Doctor, UserRole
from utils import hash_password


def create_seed_users():
    """Create default test users with credentials."""
    
    # Initialize database tables
    init_db()
    
    db = SessionLocal()
    
    try:
        # Test Users Configuration
        users_config = [
            {
                "name": "Admin User",
                "email": "admin@healthcare.com",
                "password": "admin123",
                "role": UserRole.ADMIN,
                "phone": "+1-555-0100"
            },
            {
                "name": "Dr. Sarah Johnson",
                "email": "doctor@healthcare.com",
                "password": "doctor123",
                "role": UserRole.DOCTOR,
                "phone": "+1-555-0101",
                "doctor_info": {
                    "specialization": "General Medicine",
                    "license_number": "MED-2024-001",
                    "hospital_name": "City General Hospital"
                }
            },
            {
                "name": "John Patient",
                "email": "patient@healthcare.com",
                "password": "patient123",
                "role": UserRole.PATIENT,
                "phone": "+1-555-0102",
                "patient_info": {
                    "age": 35,
                    "gender": "Male",
                    "blood_group": "O+",
                    "allergies": "None",
                    "existing_conditions": "None"
                }
            }
        ]
        
        created_users = []
        
        for user_config in users_config:
            # Check if user already exists
            existing = db.query(User).filter(User.email == user_config["email"]).first()
            if existing:
                print(f"⚠️  User already exists: {user_config['email']}")
                continue
            
            # Create user
            user = User(
                name=user_config["name"],
                email=user_config["email"],
                password_hash=hash_password(user_config["password"]),
                role=user_config["role"],
                phone=user_config["phone"]
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create profile based on role
            if user_config["role"] == UserRole.PATIENT:
                patient_info = user_config.get("patient_info", {})
                patient = Patient(
                    user_id=user.id,
                    age=patient_info.get("age"),
                    gender=patient_info.get("gender"),
                    blood_group=patient_info.get("blood_group"),
                    allergies=patient_info.get("allergies"),
                    existing_conditions=patient_info.get("existing_conditions")
                )
                db.add(patient)
                db.commit()
                
            elif user_config["role"] == UserRole.DOCTOR:
                doctor_info = user_config.get("doctor_info", {})
                doctor = Doctor(
                    user_id=user.id,
                    specialization=doctor_info.get("specialization", "General"),
                    license_number=doctor_info.get("license_number", f"LIC-{user.id}"),
                    hospital_name=doctor_info.get("hospital_name")
                )
                db.add(doctor)
                db.commit()
            
            created_users.append({
                "email": user_config["email"],
                "password": user_config["password"],
                "role": user_config["role"].value
            })
            print(f"✅ Created {user_config['role'].value}: {user_config['email']}")
        
        if created_users:
            print("\n" + "=" * 50)
            print("🎉 Test Users Created Successfully!")
            print("=" * 50)
            print("\nCredentials:")
            print("-" * 50)
            for user in created_users:
                print(f"  Role: {user['role'].upper()}")
                print(f"  Email: {user['email']}")
                print(f"  Password: {user['password']}")
                print("-" * 50)
        else:
            print("\n⚠️  No new users created (all already exist)")
            
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding Healthcare Triage Database...")
    print()
    create_seed_users()
