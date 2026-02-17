from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from models import User, LabAppointment, LabReport, UserRole
from schemas import LabReportCreate, LabReportUpdate, LabReportResponse
from dependencies import get_current_active_user, get_lab_user
from file_storage import FileStorage

router = APIRouter(prefix="/api/reports", tags=["lab-reports"])


@router.post(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload lab report",
    description="Lab staff uploads a PDF report for a lab appointment"
)
async def upload_lab_report(
    appointment_id: int,
    file: UploadFile = File(...),
    test_results: str = None,
    notes: str = None,
    current_user: User = Depends(get_lab_user),
    db: Session = Depends(get_db)
):
    """
    Upload a lab report PDF for an appointment
    
    - **appointment_id**: ID of the lab appointment
    - **file**: PDF file to upload
    - **test_results**: Summary of test results
    - **notes**: Lab notes about the report
    """
    # Verify appointment exists and belongs to this lab
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id,
        LabAppointment.lab_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or does not belong to your lab"
        )
    
    # Check if report already exists
    existing_report = db.query(LabReport).filter(
        LabReport.appointment_id == appointment_id
    ).first()
    
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report already exists for this appointment. Use update endpoint to modify."
        )
    
    # Read file content
    file_content = await file.read()
    
    # Validate file
    mime_type = file.content_type or "application/pdf"
    FileStorage.validate_file(file_content, file.filename, mime_type)
    
    # Generate unique file name and save
    unique_filename = FileStorage.generate_file_name(file.filename)
    file_path = FileStorage.save_file(file_content, unique_filename)
    
    # Create database record
    db_report = LabReport(
        appointment_id=appointment_id,
        uploaded_by_id=current_user.id,
        file_name=unique_filename,
        file_path=file_path,
        file_size=len(file_content),
        mime_type=mime_type,
        test_results=test_results,
        notes=notes
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report


@router.get(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    summary="Get lab report",
    description="Get report details for a lab appointment"
)
async def get_lab_report(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get lab report for an appointment
    
    Only patient, assigned doctor, or lab can view the report
    """
    # Verify appointment exists
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check access permissions
    is_patient = current_user.id == appointment.patient_id
    is_doctor = current_user.id == appointment.doctor_id if appointment.doctor_id else False
    is_lab = current_user.id == appointment.lab_id
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this report"
        )
    
    # Get report
    report = db.query(LabReport).filter(
        LabReport.appointment_id == appointment_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    return report


@router.put(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    summary="Update lab report",
    description="Lab staff can update report metadata"
)
async def update_lab_report(
    appointment_id: int,
    update_data: LabReportUpdate,
    current_user: User = Depends(get_lab_user),
    db: Session = Depends(get_db)
):
    """
    Update lab report information
    
    Only lab that uploaded can update
    """
    # Verify appointment exists and belongs to this lab
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id,
        LabAppointment.lab_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or does not belong to your lab"
        )
    
    # Get report
    report = db.query(LabReport).filter(
        LabReport.appointment_id == appointment_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    # Verify lab uploaded this report
    if report.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update reports you uploaded"
        )
    
    # Update fields
    if update_data.test_results is not None:
        report.test_results = update_data.test_results
    if update_data.notes is not None:
        report.notes = update_data.notes
    
    db.commit()
    db.refresh(report)
    
    return report


@router.delete(
    "/lab/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lab report",
    description="Lab staff can delete their uploaded report"
)
async def delete_lab_report(
    appointment_id: int,
    current_user: User = Depends(get_lab_user),
    db: Session = Depends(get_db)
):
    """
    Delete a lab report
    
    Only lab that uploaded can delete
    """
    # Verify appointment exists and belongs to this lab
    appointment = db.query(LabAppointment).filter(
        LabAppointment.id == appointment_id,
        LabAppointment.lab_id == current_user.id
    ).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or does not belong to your lab"
        )
    
    # Get report
    report = db.query(LabReport).filter(
        LabReport.appointment_id == appointment_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    # Verify lab uploaded this report
    if report.uploaded_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete reports you uploaded"
        )
    
    # Delete file from storage
    FileStorage.delete_file(report.file_path)
    
    # Delete database record
    db.delete(report)
    db.commit()
    
    return None


@router.get(
    "/my-reports",
    response_model=list[LabReportResponse],
    summary="Get all my reports",
    description="Get all reports for current user"
)
async def get_my_reports(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all reports for current user
    
    - Labs see reports they uploaded
    - Patients see reports for their appointments
    - Doctors see reports for patients they referred
    """
    if current_user.role == UserRole.LAB:
        reports = db.query(LabReport).filter(
            LabReport.uploaded_by_id == current_user.id
        ).all()
    elif current_user.role == UserRole.PATIENT:
        # Get all lab appointments for patient
        patient_appointments = db.query(LabAppointment.id).filter(
            LabAppointment.patient_id == current_user.id
        ).all()
        appointment_ids = [apt[0] for apt in patient_appointments]
        
        if appointment_ids:
            reports = db.query(LabReport).filter(
                LabReport.appointment_id.in_(appointment_ids)
            ).all()
        else:
            reports = []
    elif current_user.role == UserRole.DOCTOR:
        # Get all lab appointments where doctor referred
        doctor_appointments = db.query(LabAppointment.id).filter(
            LabAppointment.doctor_id == current_user.id
        ).all()
        appointment_ids = [apt[0] for apt in doctor_appointments]
        
        if appointment_ids:
            reports = db.query(LabReport).filter(
                LabReport.appointment_id.in_(appointment_ids)
            ).all()
        else:
            reports = []
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to view reports"
        )
    
    return reports
