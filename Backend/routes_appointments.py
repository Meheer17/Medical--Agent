from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo import DESCENDING

from database import get_db, get_next_sequence_value
from models import AppointmentStatus, UserRole
from schemas import (
    DoctorAppointmentCreate, DoctorAppointmentUpdate, DoctorAppointmentResponse,
    LabAppointmentCreate, LabAppointmentUpdate, LabAppointmentResponse,
    DoctorCreateLabAppointment
)
from dependencies import get_current_active_user, get_patient_user, get_doctor_user, DictWrapper

router = APIRouter(prefix="/api/appointments", tags=["appointments"])

# ============ DOCTOR APPOINTMENT ENDPOINTS ============

@router.post(
    "/doctor",
    response_model=DoctorAppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create doctor appointment",
    description="Patient creates an appointment with a doctor"
)
async def create_doctor_appointment(
    appointment: DoctorAppointmentCreate,
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Create a new doctor appointment"""
    doctor = await db.users.find_one({
        "id": appointment.doctor_id,
        "role": UserRole.DOCTOR.value,
        "is_active": True
    })
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found or is inactive"
        )
    
    # Ensure timezone aware comparison
    appt_dt = appointment.appointment_date
    if appt_dt.tzinfo is None:
        appt_dt = appt_dt.replace(tzinfo=timezone.utc)
    
    if appt_dt <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    appt_id = await get_next_sequence_value("doctor_appointments")
    now = datetime.now(timezone.utc)

    appt_doc = {
        "id": appt_id,
        "patient_id": current_user.id,
        "doctor_id": appointment.doctor_id,
        "appointment_date": appt_dt,
        "reason": appointment.reason,
        "notes": appointment.notes,
        "status": AppointmentStatus.SCHEDULED.value,
        "created_at": now,
        "updated_at": now
    }
    
    await db.doctor_appointments.insert_one(appt_doc)
    return appt_doc

@router.get(
    "/doctor/my-appointments",
    response_model=list[DoctorAppointmentResponse],
    summary="Get my doctor appointments",
    description="Get all doctor appointments for current user (patient or doctor)"
)
async def get_my_doctor_appointments(
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get doctor appointments for current user"""
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if role_val == UserRole.PATIENT.value:
        cursor = db.doctor_appointments.find({"patient_id": current_user.id}).sort("created_at", DESCENDING)
    elif role_val == UserRole.DOCTOR.value:
        cursor = db.doctor_appointments.find({"doctor_id": current_user.id}).sort("created_at", DESCENDING)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients and doctors can view doctor appointments"
        )
    
    appointments = await cursor.to_list(length=1000)
    return appointments

@router.get(
    "/doctor/{appointment_id}",
    response_model=DoctorAppointmentResponse,
    summary="Get doctor appointment details"
)
async def get_doctor_appointment(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get details of a specific doctor appointment"""
    appointment = await db.doctor_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    if not (current_user.id == appointment["patient_id"] or current_user.id == appointment["doctor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this appointment"
        )
    
    return appointment

@router.put(
    "/doctor/{appointment_id}",
    response_model=DoctorAppointmentResponse,
    summary="Update doctor appointment"
)
async def update_doctor_appointment(
    appointment_id: int,
    update_data: DoctorAppointmentUpdate,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Update a doctor appointment"""
    appointment = await db.doctor_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    if not (current_user.id == appointment["patient_id"] or current_user.id == appointment["doctor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this appointment"
        )
    
    if appointment.get("status") == AppointmentStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a cancelled appointment"
        )
    
    updates = {}
    if update_data.appointment_date:
        appt_dt = update_data.appointment_date
        if appt_dt.tzinfo is None:
            appt_dt = appt_dt.replace(tzinfo=timezone.utc)
        if appt_dt <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment date must be in the future"
            )
        updates["appointment_date"] = appt_dt

    if update_data.reason is not None:
        updates["reason"] = update_data.reason
    if update_data.notes is not None:
        updates["notes"] = update_data.notes
    if update_data.status:
        updates["status"] = update_data.status.value if hasattr(update_data.status, 'value') else update_data.status

    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        await db.doctor_appointments.update_one({"id": appointment_id}, {"$set": updates})

    updated_doc = await db.doctor_appointments.find_one({"id": appointment_id})
    return updated_doc

@router.delete(
    "/doctor/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel doctor appointment"
)
async def cancel_doctor_appointment(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Cancel a doctor appointment"""
    appointment = await db.doctor_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    if not (current_user.id == appointment["patient_id"] or current_user.id == appointment["doctor_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this appointment"
        )
    
    if appointment.get("status") == AppointmentStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    await db.doctor_appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": AppointmentStatus.CANCELLED.value, "updated_at": datetime.now(timezone.utc)}}
    )
    return None

# ============ LAB APPOINTMENT ENDPOINTS ============

@router.post(
    "/lab",
    response_model=LabAppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lab appointment"
)
async def create_lab_appointment(
    appointment: LabAppointmentCreate,
    current_user: DictWrapper = Depends(get_patient_user),
    db = Depends(get_db)
):
    """Patient creates a lab appointment"""
    lab = await db.users.find_one({
        "id": appointment.lab_id,
        "role": UserRole.LAB.value,
        "is_active": True
    })
    
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab not found or is inactive"
        )
    
    appt_dt = appointment.appointment_date
    if appt_dt.tzinfo is None:
        appt_dt = appt_dt.replace(tzinfo=timezone.utc)

    if appt_dt <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    appt_id = await get_next_sequence_value("lab_appointments")
    now = datetime.now(timezone.utc)

    appt_doc = {
        "id": appt_id,
        "patient_id": current_user.id,
        "doctor_id": None,
        "lab_id": appointment.lab_id,
        "appointment_date": appt_dt,
        "test_type": appointment.test_type,
        "reason": appointment.reason,
        "notes": appointment.notes,
        "status": AppointmentStatus.SCHEDULED.value,
        "created_at": now,
        "updated_at": now
    }
    
    await db.lab_appointments.insert_one(appt_doc)
    return appt_doc

@router.post(
    "/lab/doctor-create",
    response_model=LabAppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Doctor creates lab appointment for patient"
)
async def doctor_create_lab_appointment(
    appointment: DoctorCreateLabAppointment,
    current_user: DictWrapper = Depends(get_doctor_user),
    db = Depends(get_db)
):
    """Doctor creates a lab appointment for a patient"""
    patient = await db.users.find_one({
        "id": appointment.patient_id,
        "role": UserRole.PATIENT.value,
        "is_active": True
    })
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or is inactive"
        )
    
    lab = await db.users.find_one({
        "id": appointment.lab_id,
        "role": UserRole.LAB.value,
        "is_active": True
    })
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab not found or is inactive"
        )
    
    appt_dt = appointment.appointment_date
    if appt_dt.tzinfo is None:
        appt_dt = appt_dt.replace(tzinfo=timezone.utc)

    if appt_dt <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    appt_id = await get_next_sequence_value("lab_appointments")
    now = datetime.now(timezone.utc)

    appt_doc = {
        "id": appt_id,
        "patient_id": appointment.patient_id,
        "doctor_id": current_user.id,
        "lab_id": appointment.lab_id,
        "appointment_date": appt_dt,
        "test_type": appointment.test_type,
        "reason": appointment.reason,
        "notes": appointment.notes,
        "status": AppointmentStatus.SCHEDULED.value,
        "created_at": now,
        "updated_at": now
    }
    
    await db.lab_appointments.insert_one(appt_doc)
    return appt_doc

@router.get(
    "/lab/my-appointments",
    response_model=list[LabAppointmentResponse],
    summary="Get my lab appointments"
)
async def get_my_lab_appointments(
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get lab appointments for current user"""
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if role_val == UserRole.PATIENT.value:
        cursor = db.lab_appointments.find({"patient_id": current_user.id}).sort("created_at", DESCENDING)
    elif role_val == UserRole.DOCTOR.value:
        cursor = db.lab_appointments.find({"doctor_id": current_user.id}).sort("created_at", DESCENDING)
    elif role_val == UserRole.LAB.value:
        cursor = db.lab_appointments.find({"lab_id": current_user.id}).sort("created_at", DESCENDING)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to view lab appointments"
        )
    
    appointments = await cursor.to_list(length=1000)
    return appointments

@router.get(
    "/lab/{appointment_id}",
    response_model=LabAppointmentResponse,
    summary="Get lab appointment details"
)
async def get_lab_appointment(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get details of a specific lab appointment"""
    appointment = await db.lab_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    is_patient = current_user.id == appointment["patient_id"]
    is_doctor = current_user.id == appointment["doctor_id"] if appointment.get("doctor_id") else False
    is_lab = current_user.id == appointment["lab_id"]
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this appointment"
        )
    
    return appointment

@router.put(
    "/lab/{appointment_id}",
    response_model=LabAppointmentResponse,
    summary="Update lab appointment"
)
async def update_lab_appointment(
    appointment_id: int,
    update_data: LabAppointmentUpdate,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Update a lab appointment"""
    appointment = await db.lab_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    is_patient = current_user.id == appointment["patient_id"]
    is_doctor = current_user.id == appointment["doctor_id"] if appointment.get("doctor_id") else False
    is_lab = current_user.id == appointment["lab_id"]
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this appointment"
        )
    
    if appointment.get("status") == AppointmentStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a cancelled appointment"
        )
    
    updates = {}
    if update_data.appointment_date:
        appt_dt = update_data.appointment_date
        if appt_dt.tzinfo is None:
            appt_dt = appt_dt.replace(tzinfo=timezone.utc)
        if appt_dt <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Appointment date must be in the future"
            )
        updates["appointment_date"] = appt_dt

    if update_data.test_type is not None:
        updates["test_type"] = update_data.test_type
    if update_data.reason is not None:
        updates["reason"] = update_data.reason
    if update_data.notes is not None:
        updates["notes"] = update_data.notes
    if update_data.status:
        updates["status"] = update_data.status.value if hasattr(update_data.status, 'value') else update_data.status

    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        await db.lab_appointments.update_one({"id": appointment_id}, {"$set": updates})

    updated_doc = await db.lab_appointments.find_one({"id": appointment_id})
    return updated_doc

@router.delete(
    "/lab/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel lab appointment"
)
async def cancel_lab_appointment(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Cancel a lab appointment"""
    appointment = await db.lab_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    is_patient = current_user.id == appointment["patient_id"]
    is_doctor = current_user.id == appointment["doctor_id"] if appointment.get("doctor_id") else False
    is_lab = current_user.id == appointment["lab_id"]
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this appointment"
        )
    
    if appointment.get("status") == AppointmentStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    await db.lab_appointments.update_one(
        {"id": appointment_id},
        {"$set": {"status": AppointmentStatus.CANCELLED.value, "updated_at": datetime.now(timezone.utc)}}
    )
    return None
