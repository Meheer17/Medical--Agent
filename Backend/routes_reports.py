from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
import json
import logging
import os
from pymongo import DESCENDING

from database import get_db, get_next_sequence_value
from models import AppointmentStatus, UserRole
from schemas import LabReportCreate, LabReportUpdate, LabReportResponse
from dependencies import get_current_active_user, get_lab_user, DictWrapper
from file_storage import FileStorage
from pdf_processor import get_report_processor
from ai_field_validator import AIFieldValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["lab-reports"])

async def process_pdf_and_generate_analysis(report_id: int, file_path: str, db_session_factory):
    """
    Background task to extract PDF text, generate AI analysis, and
    automatically book a doctor appointment if the AI determines criticality
    is critical or medium.
    """
    try:
        processor = get_report_processor()
        db = get_db()
        
        report = await db.lab_reports.find_one({"id": report_id})
        if not report:
            logger.error(f"Report {report_id} not found")
            return
        
        appointment = await db.lab_appointments.find_one({"id": report["appointment_id"]})
        patient_id = appointment.get("patient_id") if appointment else None
        doctor_id = appointment.get("doctor_id") if appointment and appointment.get("doctor_id") else None
        
        if not doctor_id and patient_id:
            patient = await db.users.find_one({"id": patient_id})
            if patient and patient.get("linked_doctor_id"):
                doctor_id = patient["linked_doctor_id"]
        
        result = await processor.process_pdf_report(
            file_path=file_path,
            test_type="laboratory",
            patient_id=patient_id,
            doctor_id=doctor_id
        )
        
        if result.get("status") == "success":
            analysis = result["analysis"]
            
            summary = analysis.get("summary", "")
            key_findings = analysis.get("key_findings", [])
            abnormal_values = analysis.get("abnormal_values", [])
            
            key_findings_str = json.dumps(key_findings) if isinstance(key_findings, list) else json.dumps([])
            abnormal_values_str = json.dumps(abnormal_values) if isinstance(abnormal_values, list) else json.dumps([])
            
            clinical_significance = analysis.get("clinical_significance", "")
            criticality = analysis.get("criticality", "low")
            if criticality not in ("critical", "medium", "low"):
                criticality = "low"
            
            recommendation = analysis.get("doctor_recommendation", "")
            if recommendation and "doctor" not in recommendation.lower():
                recommendation += " Patient should visit their doctor for proper interpretation and guidance of these lab results."
            elif not recommendation:
                recommendation = "Patient should visit their doctor for proper interpretation and guidance of these lab results."
            
            updates = {
                "ai_summary": summary,
                "ai_key_findings": key_findings_str,
                "ai_abnormal_values": abnormal_values_str,
                "ai_clinical_significance": clinical_significance,
                "ai_criticality": criticality,
                "ai_doctor_recommendation": recommendation,
                "ai_analysis_status": "completed",
                "ai_analysis_error": None,
                "updated_at": datetime.now(timezone.utc)
            }
            
            await db.lab_reports.update_one({"id": report_id}, {"$set": updates})
            
            # AI-triggered appointment booking
            appointment_booking = analysis.get("appointment_booking", {})
            if appointment_booking.get("should_book") and doctor_id and patient_id:
                try:
                    await _book_appointment_from_ai_mongo(
                        db=db,
                        patient_id=patient_id,
                        doctor_id=doctor_id,
                        booking_info=appointment_booking,
                        report_id=report_id
                    )
                except Exception as book_err:
                    logger.error(f"Failed to book AI-triggered appointment for report {report_id}: {book_err}")
            
            logger.info(f"✓ AI analysis completed for report {report_id}")
        else:
            await db.lab_reports.update_one(
                {"id": report_id},
                {"$set": {
                    "ai_analysis_status": "failed",
                    "ai_analysis_error": result.get("error", "Unknown error processing PDF"),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
            logger.error(f"Failed to process PDF for report {report_id}: {result.get('error')}")
    except Exception as e:
        logger.error(f"Background task error for report {report_id}: {e}")
        try:
            db = get_db()
            await db.lab_reports.update_one(
                {"id": report_id},
                {"$set": {
                    "ai_analysis_status": "failed",
                    "ai_analysis_error": str(e),
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
        except Exception as inner_e:
            logger.error(f"Failed to update error status for report {report_id}: {inner_e}")

async def _book_appointment_from_ai_mongo(db, patient_id: int, doctor_id: int, booking_info: dict, report_id: int):
    criticality = booking_info.get("criticality", "medium")
    reason = booking_info.get("reason", "Follow-up on lab results")
    notes = booking_info.get("notes", "")
    appointment_date_str = booking_info.get("appointment_date")
    
    if appointment_date_str:
        appointment_date = datetime.fromisoformat(appointment_date_str)
    else:
        if criticality == "critical":
            days_offset = 1
        elif criticality == "medium":
            days_offset = 3
        else:
            return
        appointment_date = datetime.now(timezone.utc) + timedelta(days=days_offset)
        appointment_date = appointment_date.replace(hour=10, minute=0, second=0, microsecond=0)
    
    doctor = await db.users.find_one({
        "id": doctor_id,
        "role": UserRole.DOCTOR.value,
        "is_active": True
    })
    if not doctor:
        logger.warning(f"Cannot book appointment for report {report_id}: doctor {doctor_id} not found")
        return
    
    appt_id = await get_next_sequence_value("doctor_appointments")
    now = datetime.now(timezone.utc)
    ai_notes = f"[AI Auto-Booked - {criticality.upper()} criticality] {notes}".strip()
    
    appt_doc = {
        "id": appt_id,
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": appointment_date,
        "reason": reason,
        "notes": ai_notes,
        "status": AppointmentStatus.SCHEDULED.value,
        "created_at": now,
        "updated_at": now
    }
    
    await db.doctor_appointments.insert_one(appt_doc)
    logger.info(f"✓ AI auto-booked doctor appointment {appt_id} for report {report_id}")

@router.post(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload lab report"
)
async def upload_lab_report(
    appointment_id: int,
    file: UploadFile = File(...),
    test_results: str = None,
    notes: str = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: DictWrapper = Depends(get_lab_user),
    db = Depends(get_db)
):
    """Upload a lab report PDF for an appointment"""
    appointment = await db.lab_appointments.find_one({
        "id": appointment_id,
        "lab_id": current_user.id
    })
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or does not belong to your lab"
        )
    
    existing_report = await db.lab_reports.find_one({"appointment_id": appointment_id})
    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report already exists for this appointment. Use update endpoint to modify."
        )
    
    file_content = await file.read()
    mime_type = file.content_type or "application/pdf"
    FileStorage.validate_file(file_content, file.filename, mime_type)
    
    unique_filename = FileStorage.generate_file_name(file.filename)
    file_path = FileStorage.save_file(file_content, unique_filename)
    
    report_id = await get_next_sequence_value("lab_reports")
    now = datetime.now(timezone.utc)

    report_doc = {
        "id": report_id,
        "appointment_id": appointment_id,
        "uploaded_by_id": current_user.id,
        "file_name": unique_filename,
        "file_path": file_path,
        "file_size": len(file_content),
        "mime_type": mime_type,
        "test_results": test_results,
        "notes": notes,
        "ai_summary": None,
        "ai_key_findings": None,
        "ai_abnormal_values": None,
        "ai_clinical_significance": None,
        "ai_criticality": None,
        "ai_doctor_recommendation": "Patient should visit their doctor for proper interpretation and guidance of these lab results.",
        "ai_analysis_status": "pending",
        "ai_analysis_error": None,
        "created_at": now,
        "updated_at": now
    }
    
    await db.lab_reports.insert_one(report_doc)
    
    try:
        background_tasks.add_task(
            process_pdf_and_generate_analysis,
            report_id=report_id,
            file_path=file_path,
            db_session_factory=None
        )
        logger.info(f"✓ Background task queued for report {report_id} PDF analysis")
    except Exception as e:
        logger.error(f"Failed to queue background task for report {report_id}: {e}")
        await db.lab_reports.update_one(
            {"id": report_id},
            {"$set": {"ai_analysis_status": "failed", "ai_analysis_error": str(e)}}
        )
        report_doc["ai_analysis_status"] = "failed"
        report_doc["ai_analysis_error"] = str(e)

    return report_doc

@router.post(
    "/reanalyze/{appointment_id}",
    response_model=LabReportResponse,
    summary="Re-analyze report"
)
async def reanalyze_report(
    appointment_id: int,
    background_tasks: BackgroundTasks,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Re-trigger AI analysis for a report that previously failed"""
    report = await db.lab_reports.find_one({"appointment_id": appointment_id})
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    now = datetime.now(timezone.utc)
    resets = {
        "ai_analysis_status": "pending",
        "ai_analysis_error": None,
        "ai_summary": None,
        "ai_key_findings": None,
        "ai_abnormal_values": None,
        "ai_clinical_significance": None,
        "ai_criticality": None,
        "ai_doctor_recommendation": "Patient should visit their doctor for proper interpretation and guidance of these lab results.",
        "updated_at": now
    }
    
    await db.lab_reports.update_one({"appointment_id": appointment_id}, {"$set": resets})
    
    background_tasks.add_task(
        process_pdf_and_generate_analysis,
        report_id=report["id"],
        file_path=report["file_path"],
        db_session_factory=None
    )
    
    updated_doc = await db.lab_reports.find_one({"appointment_id": appointment_id})
    return updated_doc

@router.get(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    summary="Get lab report"
)
async def get_lab_report(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get lab report for an appointment"""
    appointment = await db.lab_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    is_patient = current_user.id == appointment["patient_id"]
    is_doctor = current_user.id == appointment["doctor_id"] if appointment.get("doctor_id") else False
    is_lab = current_user.id == appointment["lab_id"]
    
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if not is_doctor and role_val == UserRole.DOCTOR.value:
        patient = await db.users.find_one({"id": appointment["patient_id"]})
        if patient and patient.get("linked_doctor_id") == current_user.id:
            is_doctor = True
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this report"
        )
    
    report = await db.lab_reports.find_one({"appointment_id": appointment_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    return report

@router.put(
    "/lab/{appointment_id}",
    response_model=LabReportResponse,
    summary="Update lab report"
)
async def update_lab_report(
    appointment_id: int,
    update_data: LabReportUpdate,
    current_user: DictWrapper = Depends(get_lab_user),
    db = Depends(get_db)
):
    """Update lab report information"""
    appointment = await db.lab_appointments.find_one({
        "id": appointment_id,
        "lab_id": current_user.id
    })
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or does not belong to your lab"
        )
    
    report = await db.lab_reports.find_one({"appointment_id": appointment_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    if report["uploaded_by_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update reports you uploaded"
        )
    
    updates = {}
    if update_data.test_results is not None:
        updates["test_results"] = update_data.test_results
    if update_data.notes is not None:
        updates["notes"] = update_data.notes
    
    if updates:
        updates["updated_at"] = datetime.now(timezone.utc)
        await db.lab_reports.update_one({"appointment_id": appointment_id}, {"$set": updates})

    updated_doc = await db.lab_reports.find_one({"appointment_id": appointment_id})
    return updated_doc

@router.delete(
    "/lab/{appointment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete lab report"
)
async def delete_lab_report(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_lab_user),
    db = Depends(get_db)
):
    """Delete a lab report"""
    appointment = await db.lab_appointments.find_one({
        "id": appointment_id,
        "lab_id": current_user.id
    })
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found or does not belong to your lab"
        )
    
    report = await db.lab_reports.find_one({"appointment_id": appointment_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    if report["uploaded_by_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete reports you uploaded"
        )
    
    FileStorage.delete_file(report["file_path"])
    await db.lab_reports.delete_one({"appointment_id": appointment_id})
    return None

@router.get(
    "/my-reports",
    response_model=list[LabReportResponse],
    summary="Get all my reports"
)
async def get_my_reports(
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Get all reports for current user"""
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if role_val == UserRole.LAB.value:
        cursor = db.lab_reports.find({"uploaded_by_id": current_user.id}).sort("created_at", DESCENDING)
        reports = await cursor.to_list(length=1000)
    elif role_val == UserRole.PATIENT.value:
        patient_appts = await db.lab_appointments.find({"patient_id": current_user.id}).to_list(length=1000)
        appt_ids = [apt["id"] for apt in patient_appts]
        if appt_ids:
            cursor = db.lab_reports.find({"appointment_id": {"$in": appt_ids}}).sort("created_at", DESCENDING)
            reports = await cursor.to_list(length=1000)
        else:
            reports = []
    elif role_val == UserRole.DOCTOR.value:
        doctor_appts = await db.lab_appointments.find({"doctor_id": current_user.id}).to_list(length=1000)
        appt_ids = [apt["id"] for apt in doctor_appts]
        if appt_ids:
            cursor = db.lab_reports.find({"appointment_id": {"$in": appt_ids}}).sort("created_at", DESCENDING)
            reports = await cursor.to_list(length=1000)
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
    summary="Download report PDF"
)
async def download_report_file(
    appointment_id: int,
    current_user: DictWrapper = Depends(get_current_active_user),
    db = Depends(get_db)
):
    """Download the PDF file for a lab report"""
    appointment = await db.lab_appointments.find_one({"id": appointment_id})
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    is_patient = current_user.id == appointment["patient_id"]
    is_doctor = current_user.id == appointment["doctor_id"] if appointment.get("doctor_id") else False
    is_lab = current_user.id == appointment["lab_id"]
    
    role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    if not is_doctor and role_val == UserRole.DOCTOR.value:
        patient = await db.users.find_one({"id": appointment["patient_id"]})
        if patient and patient.get("linked_doctor_id") == current_user.id:
            is_doctor = True
    
    if not (is_patient or is_doctor or is_lab):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this report"
        )
    
    report = await db.lab_reports.find_one({"appointment_id": appointment_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No report found for this appointment"
        )
    
    file_path = report["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found on server"
        )
    
    return FileResponse(
        path=file_path,
        filename=report["file_name"],
        media_type=report.get("mime_type", "application/pdf")
    )
