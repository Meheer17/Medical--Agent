from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models import User, DoctorAppointment, LabAppointment, LabReport, AppointmentStatus, UserRole
from schemas import (
    DoctorAppointmentCreate, DoctorAppointmentUpdate, DoctorAppointmentResponse,
    LabAppointmentCreate, LabAppointmentUpdate, LabAppointmentResponse,
    DoctorCreateLabAppointment, LabReportCreate, LabReportUpdate, LabReportResponse
)
from dependencies import get_current_active_user, get_patient_user, get_doctor_user, get_lab_user
from file_storage import FileStorage

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
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Create a new doctor appointment
    
    - **doctor_id**: ID of the doctor
    - **appointment_date**: Desired appointment date and time
    - **reason**: Reason for appointment
    - **notes**: Additional notes
    """
    # Verify doctor exists and is a doctor
    doctor = db.query(User).filter(
        User.id == appointment.doctor_id,
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found or is inactive"
        )
    
    # Verify appointment date is in the future
    if appointment.appointment_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    db_appointment = DoctorAppointment(
        patient_id=current_user.id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date,
        reason=appointment.reason,
        notes=appointment.notes,
        status=AppointmentStatus.SCHEDULED
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.get(
    "/doctor/my-appointments",
    response_model=list[DoctorAppointmentResponse],
    summary="Get my doctor appointments",
    description="Get all doctor appointments for current user (patient or doctor)"
)
async def get_my_doctor_appointments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get doctor appointments for current user
    
    - Patients see their own appointments
    - Doctors see appointments where they are the doctor
    """
    if current_user.role == UserRole.PATIENT:
        appointments = db.query(DoctorAppointment).filter(
            DoctorAppointment.patient_id == current_user.id
        ).order_by(DoctorAppointment.created_at.desc()).all()
    elif current_user.role == UserRole.DOCTOR:
        appointments = db.query(DoctorAppointment).filter(
            DoctorAppointment.doctor_id == current_user.id
        ).order_by(DoctorAppointment.created_at.desc()).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients and doctors can view doctor appointments"
        )
    
    return appointments

@router.get(
    "/doctor/{appointment_id}",
    response_model=DoctorAppointmentResponse,
    summary="Get doctor appointment details"
)
async def get_doctor_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific doctor appointment
    
    Only the patient or assigned doctor can view the appointment
    """
    appointment = db.query(DoctorAppointment).filter(
        DoctorAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if user has access
    if not (current_user.id == appointment.patient_id or current_user.id == appointment.doctor_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this appointment"
        )
    
    return appointment

@router.put(
    "/doctor/{appointment_id}",
    response_model=DoctorAppointmentResponse,
    summary="Update doctor appointment",
    description="Patient or doctor can update appointment details"
)
async def update_doctor_appointment(
    appointment_id: int,
    update_data: DoctorAppointmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a doctor appointment
    
    - Patient can update their own appointments
    - Doctor can update appointments assigned to them
    """
    appointment = db.query(DoctorAppointment).filter(
        DoctorAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions
    if not (current_user.id == appointment.patient_id or current_user.id == appointment.doctor_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this appointment"
        )
    
    # Check if appointment is already cancelled
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a cancelled appointment"
        )
    
    # Validate future date if updating appointment_date
    if update_data.appointment_date and update_data.appointment_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    # Update fields
    if update_data.appointment_date:
        appointment.appointment_date = update_data.appointment_date
    if update_data.reason is not None:
        appointment.reason = update_data.reason
    if update_data.notes is not None:
        appointment.notes = update_data.notes
    if update_data.status:
        appointment.status = update_data.status
    
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.delete(
    "/doctor/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel doctor appointment",
    description="Patient or doctor can cancel their appointment"
)
async def cancel_doctor_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a doctor appointment
    
    - Patient can cancel their own appointments
    - Doctor can cancel appointments assigned to them
    """
    appointment = db.query(DoctorAppointment).filter(
        DoctorAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions
    if not (current_user.id == appointment.patient_id or current_user.id == appointment.doctor_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this appointment"
        )
    
    # Check if already cancelled
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    
    return None

# ============ LAB APPOINTMENT ENDPOINTS ============

@router.post(
    "/lab",
    response_model=LabAppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create lab appointment",
    description="Patient creates a lab appointment"
)
async def create_lab_appointment(
    appointment: LabAppointmentCreate,
    current_user: User = Depends(get_patient_user),
    db: Session = Depends(get_db)
):
    """
    Patient creates a lab appointment
    
    - **lab_id**: ID of the lab
    - **appointment_date**: Desired appointment date and time
    - **test_type**: Type of test to be performed
    - **reason**: Reason for the test
    - **notes**: Additional notes
    """
    # Verify lab exists and is a lab
    lab = db.query(User).filter(
        User.id == appointment.lab_id,
        User.role == UserRole.LAB,
        User.is_active == True
    ).first()
    
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab not found or is inactive"
        )
    
    # Verify appointment date is in the future
    if appointment.appointment_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    db_appointment = LabAppointment(
        patient_id=current_user.id,
        doctor_id=None,
        lab_id=appointment.lab_id,
        appointment_date=appointment.appointment_date,
        test_type=appointment.test_type,
        reason=appointment.reason,
        notes=appointment.notes,
        status=AppointmentStatus.SCHEDULED
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.post(
    "/lab/doctor-create",
    response_model=LabAppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Doctor creates lab appointment for patient",
    description="Doctor creates a lab appointment for their patient"
)
async def doctor_create_lab_appointment(
    appointment: DoctorCreateLabAppointment,
    current_user: User = Depends(get_doctor_user),
    db: Session = Depends(get_db)
):
    """
    Doctor creates a lab appointment for a patient
    
    - **patient_id**: ID of the patient
    - **lab_id**: ID of the lab
    - **appointment_date**: Desired appointment date and time
    - **test_type**: Type of test to be performed
    - **reason**: Reason for the test
    - **notes**: Medical notes/prescription
    """
    # Verify patient exists and is a patient
    patient = db.query(User).filter(
        User.id == appointment.patient_id,
        User.role == UserRole.PATIENT,
        User.is_active == True
    ).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or is inactive"
        )
    
    # Verify lab exists and is a lab
    lab = db.query(User).filter(
        User.id == appointment.lab_id,
        User.role == UserRole.LAB,
        User.is_active == True
    ).first()
    
    if not lab:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lab not found or is inactive"
        )
    
    # Verify appointment date is in the future
    if appointment.appointment_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    db_appointment = LabAppointment(
        patient_id=appointment.patient_id,
        doctor_id=current_user.id,
        lab_id=appointment.lab_id,
        appointment_date=appointment.appointment_date,
        test_type=appointment.test_type,
        reason=appointment.reason,
        notes=appointment.notes,
        status=AppointmentStatus.SCHEDULED
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment

@router.get(
    "/lab/my-appointments",
    response_model=list[LabAppointmentResponse],
    summary="Get my lab appointments",
    description="Get all lab appointments for current user (patient, doctor, or lab)"
)
async def get_my_lab_appointments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get lab appointments for current user
    
    - Patients see their own lab appointments
    - Doctors see lab appointments they created for their patients
    - Labs see appointments at their facility
    """
    if current_user.role == UserRole.PATIENT:
        appointments = db.query(LabAppointment).filter(
            LabAppointment.patient_id == current_user.id
        ).order_by(LabAppointment.created_at.desc()).all()
    elif current_user.role == UserRole.DOCTOR:
        appointments = db.query(LabAppointment).filter(
            LabAppointment.doctor_id == current_user.id
        ).order_by(LabAppointment.created_at.desc()).all()
    elif current_user.role == UserRole.LAB:
        appointments = db.query(LabAppointment).filter(
            LabAppointment.lab_id == current_user.id
        ).order_by(LabAppointment.created_at.desc()).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to view lab appointments"
        )
    
    return appointments

@router.get(
    "/lab/{appointment_id}",
    response_model=LabAppointmentResponse,
    summary="Get lab appointment details"
)
async def get_lab_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific lab appointment
    
    Patient, assigned doctor, or lab can view the appointment
    """
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if user has access
    is_patient = current_user.id == appointment.patient_id
    is_doctor = current_user.id == appointment.doctor_id if appointment.doctor_id else False
    is_lab = current_user.id == appointment.lab_id
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this appointment"
        )
    
    return appointment

@router.put(
    "/lab/{appointment_id}",
    response_model=LabAppointmentResponse,
    summary="Update lab appointment",
    description="Patient, doctor, or lab can update appointment"
)
async def update_lab_appointment(
    appointment_id: int,
    update_data: LabAppointmentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a lab appointment
    
    - Patient can update their own appointments
    - Doctor can update appointments they created
    - Lab can update appointments at their facility
    """
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions
    is_patient = current_user.id == appointment.patient_id
    is_doctor = current_user.id == appointment.doctor_id if appointment.doctor_id else False
    is_lab = current_user.id == appointment.lab_id
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this appointment"
        )
    
    # Check if appointment is already cancelled
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a cancelled appointment"
        )
    
    # Validate future date if updating appointment_date
    if update_data.appointment_date and update_data.appointment_date <= datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment date must be in the future"
        )
    
    # Update fields
    if update_data.appointment_date:
        appointment.appointment_date = update_data.appointment_date
    if update_data.test_type is not None:
        appointment.test_type = update_data.test_type
    if update_data.reason is not None:
        appointment.reason = update_data.reason
    if update_data.notes is not None:
        appointment.notes = update_data.notes
    if update_data.status:
        appointment.status = update_data.status
    
    db.commit()
    db.refresh(appointment)
    
    return appointment

@router.delete(
    "/lab/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel lab appointment",
    description="Patient, doctor, or lab can cancel appointment"
)
async def cancel_lab_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a lab appointment
    
    - Patient can cancel their own appointments
    - Doctor can cancel appointments they created
    - Lab can cancel appointments at their facility
    """
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check permissions
    is_patient = current_user.id == appointment.patient_id
    is_doctor = current_user.id == appointment.doctor_id if appointment.doctor_id else False
    is_lab = current_user.id == appointment.lab_id
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to cancel this appointment"
        )
    
    # Check if already cancelled
    if appointment.status == AppointmentStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment is already cancelled"
        )
    
    appointment.status = AppointmentStatus.CANCELLED
    db.commit()
    
    return None
