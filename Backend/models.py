from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import uuid

class UserRole(str, enum.Enum):
    """User role enumeration"""
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"
    LAB = "LAB"

class AppointmentStatus(str, enum.Enum):
    """Appointment status enumeration"""
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class QueryUrgency(str, enum.Enum):
    """Query urgency levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class User(Base):
    """User model for storing user information"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)
    doctor_code = Column(String(20), unique=True, nullable=True, index=True)  # Unique code for doctors
    linked_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # For patients linking to doctors
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    doctor_appointments_created = relationship("DoctorAppointment", foreign_keys="DoctorAppointment.patient_id", back_populates="patient")
    doctor_appointments_assigned = relationship("DoctorAppointment", foreign_keys="DoctorAppointment.doctor_id", back_populates="doctor")
    lab_appointments_created = relationship("LabAppointment", foreign_keys="LabAppointment.patient_id", back_populates="patient")
    lab_appointments_assigned = relationship("LabAppointment", foreign_keys="LabAppointment.doctor_id", back_populates="doctor")
    lab_appointments_lab = relationship("LabAppointment", foreign_keys="LabAppointment.lab_id", back_populates="lab")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

class DoctorAppointment(Base):
    """Model for doctor appointments"""
    __tablename__ = "doctor_appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="doctor_appointments_created")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_appointments_assigned")
    
    def __repr__(self):
        return f"<DoctorAppointment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, status={self.status})>"

class LabAppointment(Base):
    """Model for lab appointments"""
    __tablename__ = "lab_appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Doctor creating appointment for patient
    lab_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    test_type = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], back_populates="lab_appointments_created")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="lab_appointments_assigned")
    lab = relationship("User", foreign_keys=[lab_id], back_populates="lab_appointments_lab")
    reports = relationship("LabReport", back_populates="appointment")
    
    def __repr__(self):
        return f"<LabAppointment(id={self.id}, patient_id={self.patient_id}, lab_id={self.lab_id}, status={self.status})>"

class LabReport(Base):
    """Model for lab test reports"""
    __tablename__ = "lab_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("lab_appointments.id"), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    mime_type = Column(String(50), default="application/pdf", nullable=False)
    test_results = Column(Text, nullable=True)  # Summary or key findings
    notes = Column(Text, nullable=True)  # Lab notes about the report
    
    # AI-Generated Analysis Fields (Genkit)
    ai_summary = Column(Text, nullable=True)  # AI-generated summary of report
    ai_key_findings = Column(Text, nullable=True)  # JSON array of key findings
    ai_abnormal_values = Column(Text, nullable=True)  # JSON array of abnormal values
    ai_clinical_significance = Column(Text, nullable=True)  # AI interpretation
    ai_criticality = Column(String(50), default="low", nullable=True)  # critical, medium, low
    ai_doctor_recommendation = Column(Text, nullable=True)  # Always includes recommendation to visit doctor
    ai_analysis_status = Column(String(50), default="pending", nullable=False)  # pending, completed, failed
    ai_analysis_error = Column(Text, nullable=True)  # Error message if analysis failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    appointment = relationship("LabAppointment", back_populates="reports")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])
    
    def __repr__(self):
        return f"<LabReport(id={self.id}, appointment_id={self.appointment_id}, file_name={self.file_name}, ai_status={self.ai_analysis_status})>"

class Query(Base):
    """Model for single queries from patient to doctor"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=True)
    urgency = Column(Enum(QueryUrgency), default=QueryUrgency.MEDIUM, nullable=False)
    is_responded = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    responded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id], backref="queries_sent")
    doctor = relationship("User", foreign_keys=[doctor_id], backref="queries_received")
    
    def __repr__(self):
        return f"<Query(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, urgency={self.urgency})>"
