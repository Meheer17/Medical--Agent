from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import secrets

from database import get_db
from models import User, UserRole, LabAppointment, DoctorAppointment, LabReport
from schemas import PatientProfileUpdate, LinkDoctorRequest, PatientProfileResponse, LabReportResponse, DoctorAppointmentResponse, LabAppointmentResponse
from dependencies import get_current_active_user, get_patient_user, get_doctor_user

router = APIRouter(prefix="/api/profiles", tags=["profiles"])


def generate_doctor_code() -> str:
    """Generate a unique doctor code"""
    return "DOC" + secrets.token_hex(8).upper()


@router.get(
    "/me",
    response_model=PatientProfileResponse,
    summary="Get my profile",
    description="Get current user's profile information"
)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's profile"""
    return current_user


@router.put(
    "/me",
    response_model=PatientProfileResponse,
    summary="Update my profile",
    description="Update patient profile information"
)
async def update_my_profile(
    profile_update: PatientProfileUpdate,
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Update patient profile
    
    - **full_name**: Full name
    - **phone**: Phone number
    - **address**: Home address
    """
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    if profile_update.phone is not None:
        current_user.phone = profile_update.phone
    if profile_update.address is not None:
        current_user.address = profile_update.address
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post(
    "/link-doctor",
    response_model=PatientProfileResponse,
    summary="Link to a doctor",
    description="Link current patient to a doctor using doctor code"
)
async def link_to_doctor(
    request: LinkDoctorRequest,
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Link patient to a doctor using the doctor's unique code
    
    - **doctor_code**: Unique code provided by the doctor
    """
    # Find doctor by code
    doctor = db.query(User).filter(
        User.doctor_code == request.doctor_code,
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found with provided code or is inactive"
        )
    
    # Link patient to doctor
    current_user.linked_doctor_id = doctor.id
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.get(
    "/doctors",
    tags=["profiles"],
    summary="List all doctors",
    description="Get a list of all active doctors"
)
async def list_all_doctors(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all active doctors (available to any authenticated user)"""
    doctors = db.query(User).filter(
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).all()
    return [
        {
            "id": d.id,
            "name": d.full_name or d.username,
            "email": d.email,
            "username": d.username,
            "phone": d.phone
        }
        for d in doctors
    ]


@router.get(
    "/labs",
    tags=["profiles"],
    summary="List all labs",
    description="Get a list of all active labs"
)
async def list_all_labs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all active labs (available to any authenticated user)"""
    labs = db.query(User).filter(
        User.role == UserRole.LAB,
        User.is_active == True
    ).all()
    return [
        {
            "id": l.id,
            "name": l.full_name or l.username,
            "email": l.email,
            "username": l.username,
            "phone": l.phone
        }
        for l in labs
    ]


@router.get(
    "/my-code",
    tags=["profiles"],
    summary="Get my doctor code",
    description="Get the unique doctor code (doctors only)"
)
async def get_my_doctor_code(
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Get my doctor code
    
    This code should be shared with patients to link them to you
    """
    if not current_user.doctor_code:
        # Generate code if not exists
        code = generate_doctor_code()
        current_user.doctor_code = code
        db.commit()
        db.refresh(current_user)
    
    return {
        "doctor_id": current_user.id,
        "doctor_code": current_user.doctor_code,
        "message": "Share this code with patients to let them link to you"
    }


@router.get(
    "/regenerate-code",
    tags=["profiles"],
    summary="Regenerate doctor code",
    description="Generate a new doctor code"
)
async def regenerate_doctor_code(
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate a new doctor code
    
    The old code will be invalidated
    """
    code = generate_doctor_code()
    current_user.doctor_code = code
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "doctor_id": current_user.id,
        "doctor_code": current_user.doctor_code,
        "message": "New code generated. Share it with patients."
    }


@router.get(
    "/my-patients",
    tags=["profiles"],
    summary="Get my linked patients",
    description="Get all patients linked to current doctor"
)
async def get_my_patients(
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Get all patients linked to this doctor
    """
    patients = db.query(User).filter(
        User.linked_doctor_id == current_user.id,
        User.role == UserRole.PATIENT
    ).all()
    
    return {
        "doctor_id": current_user.id,
        "patient_count": len(patients),
        "patients": patients
    }


@router.get(
    "/patient/{patient_id}",
    tags=["profiles"],
    summary="Get patient details",
    description="Get details of a patient linked to current doctor"
)
async def get_patient_by_id(
    patient_id: int,
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a patient
    
    Doctor can only view patients linked to them
    """
    patient = db.query(User).filter(
        User.id == patient_id,
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if patient is linked to this doctor
    if patient.linked_doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient is not linked to you"
        )
    
    return patient


@router.get(
    "/my-linked-doctor",
    response_model=dict,
    tags=["profiles"],
    summary="Get my linked doctor",
    description="Get details of linked doctor (patients only)"
)
async def get_my_linked_doctor(
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Get details of my linked doctor
    """
    if not current_user.linked_doctor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't linked to any doctor yet"
        )
    
    doctor = db.query(User).filter(
        User.id == current_user.linked_doctor_id
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked doctor not found"
        )
    
    return {
        "doctor_id": doctor.id,
        "name": doctor.full_name or doctor.username,
        "email": doctor.email,
        "username": doctor.username,
        "phone": doctor.phone
    }


@router.post(
    "/unlink-doctor",
    tags=["profiles"],
    summary="Unlink from doctor",
    description="Remove link to current doctor"
)
async def unlink_from_doctor(
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Unlink from current doctor
    """
    if not current_user.linked_doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not linked to any doctor"
        )
    
    current_user.linked_doctor_id = None
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Successfully unlinked from doctor"}


@router.get(
    "/patient/{patient_id}/reports",
    response_model=list[LabReportResponse],
    tags=["profiles"],
    summary="Get patient reports",
    description="Doctor gets all lab reports for a linked patient"
)
async def get_patient_reports(
    patient_id: int,
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """Get all lab reports for a specific patient linked to this doctor"""
    patient = db.query(User).filter(
        User.id == patient_id,
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.linked_doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Patient is not linked to you")

    patient_appointments = db.query(LabAppointment.id).filter(
        LabAppointment.patient_id == patient_id
    ).all()
    appointment_ids = [a[0] for a in patient_appointments]
    if not appointment_ids:
        return []
    reports = db.query(LabReport).filter(
        LabReport.appointment_id.in_(appointment_ids)
    ).order_by(LabReport.created_at.desc()).all()
    return reports


@router.get(
    "/patient/{patient_id}/doctor-appointments",
    response_model=list[DoctorAppointmentResponse],
    tags=["profiles"],
    summary="Get patient doctor appointments",
    description="Doctor gets all doctor appointments for a linked patient"
)
async def get_patient_doctor_appointments(
    patient_id: int,
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """Get all doctor appointments for a specific patient"""
    patient = db.query(User).filter(
        User.id == patient_id,
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.linked_doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Patient is not linked to you")

    appointments = db.query(DoctorAppointment).filter(
        DoctorAppointment.patient_id == patient_id
    ).order_by(DoctorAppointment.created_at.desc()).all()
    return appointments


@router.get(
    "/patient/{patient_id}/lab-appointments",
    response_model=list[LabAppointmentResponse],
    tags=["profiles"],
    summary="Get patient lab appointments",
    description="Doctor gets all lab appointments for a linked patient"
)
async def get_patient_lab_appointments(
    patient_id: int,
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """Get all lab appointments for a specific patient"""
    patient = db.query(User).filter(
        User.id == patient_id,
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.linked_doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Patient is not linked to you")

    appointments = db.query(LabAppointment).filter(
        LabAppointment.patient_id == patient_id
    ).order_by(LabAppointment.created_at.desc()).all()
    return appointments
