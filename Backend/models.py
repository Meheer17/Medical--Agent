import enum

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
