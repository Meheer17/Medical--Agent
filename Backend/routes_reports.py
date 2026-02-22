from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import json
import logging
import os
from datetime import datetime

from database import get_db
from models import User, LabAppointment, LabReport, DoctorAppointment, AppointmentStatus, UserRole
from schemas import LabReportCreate, LabReportUpdate, LabReportResponse
from dependencies import get_current_active_user, get_lab_user
from file_storage import FileStorage
from pdf_processor import get_report_processor
from ai_field_validator import AIFieldValidator, validate_and_ensure_fields

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["lab-reports"])


async def process_pdf_and_generate_analysis(report_id: int, file_path: str, db_session_factory):
    """
    Background task to extract PDF text, generate AI analysis, and
    automatically book a doctor appointment if the AI determines criticality
    is critical or medium (via function calling / MCP tool).
    
    Args:
        report_id: ID of the report to update
        file_path: Path to the uploaded PDF file
        db_session_factory: Database session factory
    """
    try:
        processor = get_report_processor()
        
        # Look up patient_id and doctor_id from the report's appointment
        from database import SessionLocal
        db = SessionLocal()
        try:
            report = db.query(LabReport).filter(LabReport.id == report_id).first()
            if not report:
                logger.error(f"Report {report_id} not found")
                return
            
            appointment = db.query(LabAppointment).filter(
                LabAppointment.id == report.appointment_id
            ).first()
            
            patient_id = appointment.patient_id if appointment else None
            # Use the appointment's doctor_id, or fall back to the patient's linked doctor
            doctor_id = appointment.doctor_id if appointment and appointment.doctor_id else None
            if not doctor_id and patient_id:
                patient = db.query(User).filter(User.id == patient_id).first()
                if patient and patient.linked_doctor_id:
                    doctor_id = patient.linked_doctor_id
        finally:
            db.close()
        
        # Process PDF and generate analysis (AI decides on appointment booking via tool)
        result = await processor.process_pdf_report(
            file_path=file_path,
            test_type="laboratory",
            patient_id=patient_id,
            doctor_id=doctor_id
        )
        
        if result["status"] == "success":
            analysis = result["analysis"]
            
            # Update database with AI analysis
            db = SessionLocal()
            try:
                report = db.query(LabReport).filter(LabReport.id == report_id).first()
                if report:
                    # Map all AI analysis fields from result
                    report.ai_summary = analysis.get("summary", "")
                    
                    # Ensure key_findings is properly JSON stringified
                    key_findings = analysis.get("key_findings", [])
                    if isinstance(key_findings, list):
                        report.ai_key_findings = json.dumps(key_findings)
                    else:
                        report.ai_key_findings = json.dumps([])
                    
                    # Ensure abnormal_values is properly JSON stringified
                    abnormal_values = analysis.get("abnormal_values", [])
                    if isinstance(abnormal_values, list):
                        report.ai_abnormal_values = json.dumps(abnormal_values)
                    else:
                        report.ai_abnormal_values = json.dumps([])
                    
                    report.ai_clinical_significance = analysis.get("clinical_significance", "")
                    
                    # Store criticality assessment from AI
                    criticality = analysis.get("criticality", "low")
                    if criticality not in ("critical", "medium", "low"):
                        criticality = "low"
                    report.ai_criticality = criticality
                    
                    # Ensure doctor recommendation always includes visit recommendation
                    recommendation = analysis.get("doctor_recommendation", "")
                    if recommendation and "doctor" not in recommendation.lower():
                        recommendation += " Patient should visit their doctor for proper interpretation and guidance of these lab results."
                    elif not recommendation:
                        recommendation = "Patient should visit their doctor for proper interpretation and guidance of these lab results."
                    report.ai_doctor_recommendation = recommendation
                    
                    # Mark analysis as completed
                    report.ai_analysis_status = "completed"
                    report.ai_analysis_error = None
                    
                    # Commit all changes
                    db.commit()
                    
                    # Handle AI-triggered appointment booking
                    appointment_booking = analysis.get("appointment_booking", {})
                    if appointment_booking.get("should_book") and doctor_id and patient_id:
                        try:
                            _book_appointment_from_ai(
                                db=db,
                                patient_id=patient_id,
                                doctor_id=doctor_id,
                                booking_info=appointment_booking,
                                report_id=report_id
                            )
                        except Exception as book_err:
                            logger.error(f"Failed to book AI-triggered appointment for report {report_id}: {book_err}")
                    elif appointment_booking.get("should_book") and not doctor_id:
                        logger.warning(f"AI wants to book appointment for report {report_id} but no doctor is linked to the patient")
                    
                    # Validate that all fields were properly stored
                    db.refresh(report)
                    validation_result = AIFieldValidator.validate_report_record(report)
                    if validation_result['is_valid']:
                        logger.info(f"✓ AI analysis completed and validated for report {report_id}")
                    else:
                        logger.warning(f"⚠ Validation warnings for report {report_id}: {validation_result['all_errors']}")
                    
                    logger.debug(f"Fields stored - Summary: {len(report.ai_summary or '')} chars, Key findings: {report.ai_key_findings}, Abnormal values: {report.ai_abnormal_values}")
                else:
                    logger.error(f"Report {report_id} not found in database after successful processing")
            except Exception as e:
                logger.error(f"Error updating report {report_id} with AI analysis: {e}")
                # Update report with error status
                try:
                    report = db.query(LabReport).filter(LabReport.id == report_id).first()
                    if report:
                        report.ai_analysis_status = "failed"
                        report.ai_analysis_error = str(e)
                        db.commit()
                        logger.error(f"Report {report_id} marked as failed due to storage error")
                except Exception as inner_e:
                    logger.error(f"Failed to update error status for report {report_id}: {inner_e}")
                finally:
                    db.close()
            finally:
                if db and hasattr(db, 'close'):
                    db.close()
        else:
            # PDF processing failed, mark report with error
            from database import SessionLocal
            db = SessionLocal()
            try:
                report = db.query(LabReport).filter(LabReport.id == report_id).first()
                if report:
                    report.ai_analysis_status = "failed"
                    report.ai_analysis_error = result.get("error", "Unknown error processing PDF")
                    db.commit()
                    logger.error(f"Failed to process PDF for report {report_id}: {result.get('error')}")
                else:
                    logger.error(f"Report {report_id} not found to mark as failed")
            except Exception as e:
                logger.error(f"Error updating error status for report {report_id}: {e}")
            finally:
                if db and hasattr(db, 'close'):
                    db.close()
    
    except Exception as e:
        logger.error(f"Background task error for report {report_id}: {e}")
        # Try to update report with error
        try:
            from database import SessionLocal
            db = SessionLocal()
            try:
                report = db.query(LabReport).filter(LabReport.id == report_id).first()
                if report:
                    report.ai_analysis_status = "failed"
                    report.ai_analysis_error = str(e)
                    db.commit()
                    logger.error(f"Report {report_id} marked as failed with error: {str(e)}")
                else:
                    logger.error(f"Could not find report {report_id} to mark as failed")
            finally:
                db.close()
        except Exception as inner_e:
            logger.error(f"Failed to update error status for report {report_id}: {inner_e}")


def _book_appointment_from_ai(db, patient_id: int, doctor_id: int, booking_info: dict, report_id: int):
    """
    Book a doctor appointment triggered by the AI model's tool call.
    
    Criticality-based scheduling:
    - critical: appointment the very next day at 10:00 AM
    - medium: appointment after 3 days at 10:00 AM
    - low: no appointment (should not reach here)
    
    Args:
        db: Database session
        patient_id: Patient's user ID
        doctor_id: Doctor's user ID
        booking_info: Dict with appointment details from AI tool call
        report_id: Report ID for logging
    """
    from datetime import timedelta
    
    criticality = booking_info.get("criticality", "medium")
    reason = booking_info.get("reason", "Follow-up on lab results")
    notes = booking_info.get("notes", "")
    appointment_date_str = booking_info.get("appointment_date")
    
    if appointment_date_str:
        appointment_date = datetime.fromisoformat(appointment_date_str)
    else:
        # Fallback: compute from criticality
        if criticality == "critical":
            days_offset = 1
        elif criticality == "medium":
            days_offset = 3
        else:
            logger.info(f"Skipping appointment booking for report {report_id} (criticality: {criticality})")
            return
        appointment_date = datetime.now() + timedelta(days=days_offset)
        appointment_date = appointment_date.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Verify doctor exists and is active
    doctor = db.query(User).filter(
        User.id == doctor_id,
        User.role == UserRole.DOCTOR,
        User.is_active == True
    ).first()
    
    if not doctor:
        logger.warning(f"Cannot book appointment for report {report_id}: doctor {doctor_id} not found or inactive")
        return
    
    # Create the doctor appointment
    ai_notes = f"[AI Auto-Booked - {criticality.upper()} criticality] {notes}".strip()
    
    db_appointment = DoctorAppointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        reason=reason,
        notes=ai_notes,
        status=AppointmentStatus.SCHEDULED
    )
    
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    logger.info(
        f"✓ AI auto-booked doctor appointment {db_appointment.id} for report {report_id} "
        f"(criticality: {criticality}, date: {appointment_date}, patient: {patient_id}, doctor: {doctor_id})"
    )


@router.post(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload lab report",
    description="Lab staff uploads a PDF report for a lab appointment. PDF will be automatically analyzed using AI."
)
async def upload_lab_report(
    appointment_id: int,
    file: UploadFile = File(...),
    test_results: str = None,
    notes: str = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_lab_user),
    db: Session = Depends(get_db)
):
    """
    Upload a lab report PDF for an appointment
    
    **Features:**
    - Accepts PDF files only
    - Automatically extracts text from PDF
    - Uses Google AI (Genkit) to generate analysis and summary
    - Always includes recommendation to visit doctor
    - Processing happens in background (report created immediately)
    
    **Parameters:**
    - **appointment_id**: ID of the lab appointment
    - **file**: PDF file to upload
    - **test_results**: Optional summary of test results
    - **notes**: Optional lab notes about the report
    
    **Returns:**
    - Initial report object with `ai_analysis_status: "pending"`
    - AI analysis fields will be populated once background processing completes
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
    
    # Create database record with pending AI analysis status
    # Initialize all AI fields to ensure proper storage
    db_report = LabReport(
        appointment_id=appointment_id,
        uploaded_by_id=current_user.id,
        file_name=unique_filename,
        file_path=file_path,
        file_size=len(file_content),
        mime_type=mime_type,
        test_results=test_results,
        notes=notes,
        # Initialize all AI analysis fields
        ai_summary=None,
        ai_key_findings=None,
        ai_abnormal_values=None,
        ai_clinical_significance=None,
        ai_criticality=None,
        ai_doctor_recommendation="Patient should visit their doctor for proper interpretation and guidance of these lab results.",
        ai_analysis_status="pending",
        ai_analysis_error=None
    )
    
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    # Validate that all fields were properly stored
    validation_result = AIFieldValidator.validate_report_record(db_report)
    if not validation_result['is_valid']:
        logger.warning(f"⚠ Initial validation warnings for report {db_report.id}: {validation_result['all_errors']}")
    else:
        logger.info(f"✓ Report {db_report.id} initial field validation passed")
    
    # Add background task to process PDF and generate AI analysis
    try:
        background_tasks.add_task(
            process_pdf_and_generate_analysis,
            report_id=db_report.id,
            file_path=file_path,
            db_session_factory=None  # Not needed with current implementation
        )
        logger.info(f"✓ Background task queued for report {db_report.id} PDF analysis")
    except Exception as e:
        logger.error(f"Failed to queue background task for report {db_report.id}: {e}")
        # Update report to show error
        db_report.ai_analysis_status = "failed"
        db_report.ai_analysis_error = f"Failed to queue analysis: {str(e)}"
        db.commit()
        db.refresh(db_report)
    
    return db_report


@router.post(
    "/reanalyze/{appointment_id}",
    response_model=LabReportResponse,
    summary="Re-analyze report",
    description="Re-trigger AI analysis for a failed report"
)
async def reanalyze_report(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Re-trigger AI analysis for a report that previously failed"""
    report = db.query(LabReport).filter(
        LabReport.appointment_id == appointment_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    # Reset AI fields
    report.ai_analysis_status = "pending"
    report.ai_analysis_error = None
    report.ai_summary = None
    report.ai_key_findings = None
    report.ai_abnormal_values = None
    report.ai_clinical_significance = None
    report.ai_criticality = None
    report.ai_doctor_recommendation = "Patient should visit their doctor for proper interpretation and guidance of these lab results."
    db.commit()
    db.refresh(report)
    
    # Queue background analysis
    background_tasks.add_task(
        process_pdf_and_generate_analysis,
        report_id=report.id,
        file_path=report.file_path,
        db_session_factory=None
    )
    logger.info(f"✓ Re-analysis queued for report {report.id}")
    
    return report


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
    
    Only patient, assigned doctor, linked doctor, or lab can view the report
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
    
    # Also allow the patient's linked doctor
    if not is_doctor and current_user.role == UserRole.DOCTOR:
        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        if patient and patient.linked_doctor_id == current_user.id:
            is_doctor = True
    
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
        ).order_by(LabReport.created_at.desc()).all()
    elif current_user.role == UserRole.PATIENT:
        # Get all lab appointments for patient
        patient_appointments = db.query(LabAppointment.id).filter(
            LabAppointment.patient_id == current_user.id
        ).all()
        appointment_ids = [apt[0] for apt in patient_appointments]
        
        if appointment_ids:
            reports = db.query(LabReport).filter(
                LabReport.appointment_id.in_(appointment_ids)
            ).order_by(LabReport.created_at.desc()).all()
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
            ).order_by(LabReport.created_at.desc()).all()
        else:
            reports = []
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized to view reports"
        )
    
    return reports


@router.get(
    "/download/{appointment_id}",
    summary="Download report PDF",
    description="Download the PDF file for a lab report"
)
async def download_report_file(
    appointment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download the PDF file for a lab report.
    
    Only patient, assigned doctor, linked doctor, or lab can download the file.
    """
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
    
    # Also allow the patient's linked doctor
    if not is_doctor and current_user.role == UserRole.DOCTOR:
        patient = db.query(User).filter(User.id == appointment.patient_id).first()
        if patient and patient.linked_doctor_id == current_user.id:
            is_doctor = True
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this report"
        )
    
    report = db.query(LabReport).filter(
        LabReport.appointment_id == appointment_id
    ).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    file_path = report.file_path
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on server"
        )
    
    return FileResponse(
        path=file_path,
        filename=report.file_name,
        media_type=report.mime_type
    )
