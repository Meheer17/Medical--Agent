from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRoleEnum(str, Enum):
    """User role enumeration for Pydantic"""
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"
    LAB = "LAB"

class QueryUrgencyEnum(str, Enum):
    """Query urgency enumeration for Pydantic"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class AppointmentStatusEnum(str, Enum):
    """Appointment status enumeration for Pydantic"""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

# Signup/Registration Schemas
class UserRegister(BaseModel):
    """Schema for user registration (signup)"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRoleEnum = Field(default=UserRoleEnum.PATIENT)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "role": "patient"
            }
        }

# Login Schema
class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }

# Token Schemas
class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "john_doe",
                    "full_name": "John Doe",
                    "role": "patient",
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00"
                }
            }
        }

# User Response Schema
class UserResponse(BaseModel):
    """Schema for user response (without password)"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "role": "patient",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00"
            }
        })

# Profile Response Schemas - Role Based
class DoctorProfile(BaseModel):
    """Schema for doctor profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRoleEnum
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
            "example": {
                "id": 1,
                "email": "doctor@example.com",
                "username": "dr_john",
                "full_name": "Dr. John Doe",
                "role": "doctor",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
        })

class PatientProfile(BaseModel):
    """Schema for patient profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
            "example": {
                "id": 2,
                "email": "patient@example.com",
                "username": "patient_jane",
                "full_name": "Jane Doe",
                "role": "patient",
                "is_active": True,
                "is_verified": True,
                "created_at": "2024-01-01T00:00:00"
            }
        })

class LabProfile(BaseModel):
    """Schema for lab profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRoleEnum
    is_active: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
            "example": {
                "id": 3,
                "email": "lab@example.com",
                "username": "lab_admin",
                "full_name": "Lab Admin",
                "role": "lab",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00"
            }
        })

# Error Response Schema
class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials",
                "error_code": "INVALID_CREDENTIALS"
            }
        }

# Doctor Appointment Schemas
class DoctorAppointmentCreate(BaseModel):
    """Schema for creating a doctor appointment"""
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "doctor_id": 1,
                "appointment_date": "2026-02-20T10:00:00",
                "reason": "Routine checkup",
                "notes": "Please arrive 10 minutes early"
            }
        }

class DoctorAppointmentUpdate(BaseModel):
    """Schema for updating a doctor appointment"""
    appointment_date: Optional[datetime] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatusEnum] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "appointment_date": "2026-02-20T11:00:00",
                "status": "confirmed"
            }
        }

class DoctorAppointmentResponse(BaseModel):
    """Schema for doctor appointment response"""
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: datetime
    reason: Optional[str]
    notes: Optional[str]
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
            "example": {
                "id": 1,
                "patient_id": 2,
                "doctor_id": 1,
                "appointment_date": "2026-02-20T10:00:00",
                "reason": "Routine checkup",
                "notes": "Please arrive 10 minutes early",
                "status": "scheduled",
                "created_at": "2026-02-17T00:00:00",
                "updated_at": "2026-02-17T00:00:00"
            }
        })

# Lab Appointment Schemas
class LabAppointmentCreate(BaseModel):
    """Schema for creating a lab appointment by patient"""
    lab_id: int
    appointment_date: datetime
    test_type: str = Field(..., min_length=1, max_length=255)
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "lab_id": 3,
                "appointment_date": "2026-02-22T14:00:00",
                "test_type": "Blood Test",
                "reason": "Routine checkup",
                "notes": "Fasting required"
            }
        }

class DoctorCreateLabAppointment(BaseModel):
    """Schema for doctor creating lab appointment for patient"""
    patient_id: int
    lab_id: int
    appointment_date: datetime
    test_type: str = Field(..., min_length=1, max_length=255)
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 2,
                "lab_id": 3,
                "appointment_date": "2026-02-22T14:00:00",
                "test_type": "Blood Test",
                "reason": "As per medical prescription"
            }
        }

class LabAppointmentUpdate(BaseModel):
    """Schema for updating a lab appointment"""
    appointment_date: Optional[datetime] = None
    test_type: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatusEnum] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "appointment_date": "2026-02-22T15:00:00",
                "status": "confirmed"
            }
        }

class LabAppointmentResponse(BaseModel):
    """Schema for lab appointment response"""
    id: int
    patient_id: int
    doctor_id: Optional[int]
    lab_id: int
    appointment_date: datetime
    test_type: str
    reason: Optional[str]
    notes: Optional[str]
    status: AppointmentStatusEnum
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
            "example": {
                "id": 1,
                "patient_id": 2,
                "doctor_id": None,
                "lab_id": 3,
                "appointment_date": "2026-02-22T14:00:00",
                "test_type": "Blood Test",
                "reason": "Routine checkup",
                "notes": "Fasting required",
                "status": "scheduled",
                "created_at": "2026-02-17T00:00:00",
                "updated_at": "2026-02-17T00:00:00"
            }
        })

# Resolve forward references (Token.user -> UserResponse)
Token.model_rebuild()

# Lab Report Schemas
class LabReportCreate(BaseModel):
    """Schema for creating a lab report"""
    test_results: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_results": "All values within normal range",
                "notes": "Patient in good health condition"
            }
        }

class LabReportUpdate(BaseModel):
    """Schema for updating a lab report"""
    test_results: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "test_results": "Updated results",
                "notes": "Additional notes"
            }
        }

class AIAnalysisResult(BaseModel):
    """Schema for AI analysis results"""
    summary: Optional[str] = None
    key_findings: Optional[list[str]] = None
    abnormal_values: Optional[list[str]] = None
    clinical_significance: Optional[str] = None
    criticality: str = "low"  # critical, medium, low
    doctor_recommendation: str = "Patient should visit their doctor for proper interpretation and guidance of these lab results."
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "Blood tests show slightly elevated glucose levels.",
                "key_findings": ["Glucose: 110 mg/dL (normal: 70-100)", "Hemoglobin: 14.5 g/dL (normal)"],
                "abnormal_values": ["Glucose: 110 mg/dL"],
                "clinical_significance": "Slightly elevated glucose may indicate prediabetic condition.",
                "criticality": "medium",
                "doctor_recommendation": "Patient should visit their doctor for proper interpretation and guidance of these lab results."
            }
        }

class LabReportResponse(BaseModel):
    """Schema for lab report response"""
    id: int
    appointment_id: int
    uploaded_by_id: int
    file_name: str
    file_size: int
    mime_type: str
    test_results: Optional[str]
    notes: Optional[str]
    
    # AI Analysis Fields
    ai_summary: Optional[str] = None
    ai_key_findings: Optional[str] = None  # JSON string
    ai_abnormal_values: Optional[str] = None  # JSON string
    ai_clinical_significance: Optional[str] = None
    ai_criticality: Optional[str] = None  # critical, medium, low
    ai_doctor_recommendation: Optional[str] = None
    ai_analysis_status: str = "pending"  # pending, completed, failed
    ai_analysis_error: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "appointment_id": 1,
                "uploaded_by_id": 3,
                "file_name": "lab_report_001.pdf",
                "file_size": 245678,
                "mime_type": "application/pdf",
                "test_results": "All values within normal range",
                "notes": "Patient in good health condition",
                "ai_summary": "Blood tests show slightly elevated glucose levels.",
                "ai_key_findings": "[\"Glucose: 110 mg/dL (normal: 70-100)\", \"Hemoglobin: 14.5 g/dL (normal)\"]",
                "ai_abnormal_values": "[\"Glucose: 110 mg/dL\"]",
                "ai_clinical_significance": "Slightly elevated glucose may indicate prediabetic condition.",
                "ai_criticality": "medium",
                "ai_doctor_recommendation": "Patient should visit their doctor for proper interpretation and guidance of these lab results.",
                "ai_analysis_status": "completed",
                "ai_analysis_error": None,
                "created_at": "2026-02-18T14:30:00",
                "updated_at": "2026-02-18T14:30:00"
            }
        }

# Patient Profile Schemas
class PatientProfileUpdate(BaseModel):
    """Schema for updating patient profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Jane Doe",
                "phone": "+1234567890",
                "address": "123 Main Street, City, Country"
            }
        }

class LinkDoctorRequest(BaseModel):
    """Schema for linking to a doctor using doctor code"""
    doctor_code: str = Field(..., min_length=1, max_length=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "doctor_code": "DOC123ABC456XYZ"
            }
        }

class PatientProfileResponse(BaseModel):
    """Schema for patient profile response"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRoleEnum
    phone: Optional[str]
    address: Optional[str]
    linked_doctor_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 2,
                "email": "patient@example.com",
                "username": "patient_jane",
                "full_name": "Jane Doe",
                "role": "patient",
                "phone": "+1234567890",
                "address": "123 Main Street",
                "linked_doctor_id": 1,
                "is_active": True,
                "created_at": "2026-02-18T00:00:00",
                "updated_at": "2026-02-18T00:00:00"
            }
        }

# Query/Message Schemas
class QueryCreate(BaseModel):
    """Schema for creating a query"""
    query_text: str = Field(..., min_length=1, max_length=1000)
    urgency: QueryUrgencyEnum = QueryUrgencyEnum.MEDIUM
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "When can we meet for consultation?",
                "urgency": "medium"
            }
        }

class QueryRespond(BaseModel):
    """Schema for doctor responding to a query"""
    response_text: str = Field(..., min_length=1, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response_text": "Tomorrow at 2:00 PM works for me"
            }
        }

class QueryResponse(BaseModel):
    """Schema for query response"""
    id: int
    patient_id: int
    doctor_id: int
    query_text: str
    response_text: Optional[str]
    urgency: QueryUrgencyEnum
    is_responded: bool
    created_at: datetime
    responded_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "patient_id": 2,
                "doctor_id": 1,
                "query_text": "When can we meet for consultation?",
                "response_text": "Tomorrow at 2:00 PM works for me",
                "urgency": "medium",
                "is_responded": True,
                "created_at": "2026-02-18T10:00:00",
                "responded_at": "2026-02-18T10:30:00"
            }
        }
