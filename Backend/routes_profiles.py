from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
import secrets
from pymongo import DESCENDING

from database import get_db
from models import UserRole
from schemas import (
    PatientProfileUpdate, LinkDoctorRequest, PatientProfileResponse,
    LabReportResponse, DoctorAppointmentResponse, LabAppointmentResponse,
    MyPatientsResponse, UserResponse
)
from dependencies import get_current_active_user, get_patient_user, get_doctor_user, DictWrapper

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
    current_user: DictWrapper = Depends(get_current_active_user)
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
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Update patient profile"""
    update_data = {}
    if profile_update.full_name is not None:
        update_data["full_name"] = profile_update.full_name
        current_user.full_name = profile_update.full_name
    if profile_update.phone is not None:
        update_data["phone"] = profile_update.phone
        current_user.phone = profile_update.phone
    if profile_update.address is not None:
        update_data["address"] = profile_update.address
        current_user.address = profile_update.address

    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc)
        await db.users.update_one({"id": current_user.id}, {"$set": update_data})
        updated_doc = await db.users.find_one({"id": current_user.id})
        return DictWrapper(updated_doc)

    return current_user

@router.post(
    "/link-doctor",
    response_model=PatientProfileResponse,
    summary="Link to a doctor",
    description="Link current patient to a doctor using doctor code"
)
async def link_to_doctor(
    request: LinkDoctorRequest,
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Link patient to a doctor using the doctor's unique code"""
    doctor = await db.users.find_one({
        "doctor_code": request.doctor_code,
        "role": UserRole.DOCTOR.value,
        "is_active": True
    })
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found with provided code or is inactive"
        )
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"linked_doctor_id": doctor["id"], "updated_at": datetime.now(timezone.utc)}}
    )
    
    updated_doc = await db.users.find_one({"id": current_user.id})
    return DictWrapper(updated_doc)

@router.get(
    "/doctors",
    tags=["profiles"],
    summary="List all doctors",
    description="Get a list of all active doctors"
)
async def list_all_doctors(
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """List all active doctors"""
    cursor = db.users.find({
        "role": UserRole.DOCTOR.value,
        "is_active": True
    })
    doctors = await cursor.to_list(length=1000)
    return [
        {
            "id": d["id"],
            "name": d.get("full_name") or d.get("username"),
            "email": d.get("email"),
            "username": d.get("username"),
            "phone": d.get("phone")
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
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """List all active labs"""
    cursor = db.users.find({
        "role": UserRole.LAB.value,
        "is_active": True
    })
    labs = await cursor.to_list(length=1000)
    return [
        {
            "id": l["id"],
            "name": l.get("full_name") or l.get("username"),
            "email": l.get("email"),
            "username": l.get("username"),
            "phone": l.get("phone")
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
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get my doctor code"""
    code = current_user.doctor_code
    if not code:
        code = generate_doctor_code()
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"doctor_code": code, "updated_at": datetime.now(timezone.utc)}}
        )
    
    return {
        "doctor_id": current_user.id,
        "doctor_code": code,
        "message": "Share this code with patients to let them link to you"
    }

@router.get(
    "/regenerate-code",
    tags=["profiles"],
    summary="Regenerate doctor code",
    description="Generate a new doctor code"
)
async def regenerate_doctor_code(
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Regenerate a new doctor code"""
    code = generate_doctor_code()
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"doctor_code": code, "updated_at": datetime.now(timezone.utc)}}
    )
    
    return {
        "doctor_id": current_user.id,
        "doctor_code": code,
        "message": "New code generated. Share it with patients."
    }

@router.get(
    "/my-patients",
    response_model=MyPatientsResponse,
    tags=["profiles"],
    summary="Get my linked patients",
    description="Get all patients linked to current doctor"
)
async def get_my_patients(
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get all patients linked to this doctor"""
    cursor = db.users.find({
        "linked_doctor_id": current_user.id,
        "role": UserRole.PATIENT.value
    })
    patients = await cursor.to_list(length=1000)
    for p in patients:
        p.pop("_id", None)
        p.pop("hashed_password", None)
    
    return {
        "doctor_id": current_user.id,
        "patient_count": len(patients),
        "patients": patients
    }

@router.get(
    "/patient/{patient_id}",
    response_model=UserResponse,
    tags=["profiles"],
    summary="Get patient details",
    description="Get details of a patient linked to current doctor"
)
async def get_patient_by_id(
    patient_id: int,
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get details of a patient"""
    patient = await db.users.find_one({
        "id": patient_id,
        "role": UserRole.PATIENT.value,
        "is_active": True
    })
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    if patient.get("linked_doctor_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient is not linked to you"
        )
    
    patient.pop("_id", None)
    patient.pop("hashed_password", None)
    return patient

@router.get(
    "/my-linked-doctor",
    response_model=dict,
    tags=["profiles"],
    summary="Get my linked doctor",
    description="Get details of linked doctor (patients only)"
)
async def get_my_linked_doctor(
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Get details of my linked doctor"""
    linked_id = current_user.get("linked_doctor_id")
    if not linked_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't linked to any doctor yet"
        )
    
    doctor = await db.users.find_one({"id": linked_id})
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Linked doctor not found"
        )
    
    return {
        "doctor_id": doctor["id"],
        "name": doctor.get("full_name") or doctor.get("username"),
        "email": doctor.get("email"),
        "username": doctor.get("username"),
        "phone": doctor.get("phone")
    }

@router.post(
    "/unlink-doctor",
    tags=["profiles"],
    summary="Unlink from doctor",
    description="Remove link to current doctor"
)
async def unlink_from_doctor(
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Unlink from current doctor"""
    if not current_user.get("linked_doctor_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not linked to any doctor"
        )
    
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"linked_doctor_id": None, "updated_at": datetime.now(timezone.utc)}}
    )
    
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
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get all lab reports for a specific patient linked to this doctor"""
    patient = await db.users.find_one({
        "id": patient_id,
        "role": UserRole.PATIENT.value,
        "is_active": True
    })
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.get("linked_doctor_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Patient is not linked to you")

    patient_appts = await db.lab_appointments.find({"patient_id": patient_id}).to_list(length=1000)
    appt_ids = [a["id"] for a in patient_appts]
    if not appt_ids:
        return []
    
    cursor = db.lab_reports.find({"appointment_id": {"$in": appt_ids}}).sort("created_at", DESCENDING)
    reports = await cursor.to_list(length=1000)
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
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get all doctor appointments for a specific patient"""
    patient = await db.users.find_one({
        "id": patient_id,
        "role": UserRole.PATIENT.value,
        "is_active": True
    })
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.get("linked_doctor_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Patient is not linked to you")

    cursor = db.doctor_appointments.find({"patient_id": patient_id}).sort("created_at", DESCENDING)
    appointments = await cursor.to_list(length=1000)
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
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Get all lab appointments for a specific patient"""
    patient = await db.users.find_one({
        "id": patient_id,
        "role": UserRole.PATIENT.value,
        "is_active": True
    })
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if patient.get("linked_doctor_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Patient is not linked to you")

    cursor = db.lab_appointments.find({"patient_id": patient_id}).sort("created_at", DESCENDING)
    appointments = await cursor.to_list(length=1000)
    return appointments
