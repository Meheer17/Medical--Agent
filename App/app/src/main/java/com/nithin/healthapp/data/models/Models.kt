package com.nithin.healthapp.data.models

import com.google.gson.annotations.SerializedName

// ========== Auth Models ==========

data class LoginRequest(
    val email: String,
    val password: String
)

data class SignupRequest(
    val email: String,
    val username: String,
    val password: String,
    @SerializedName("full_name") val fullName: String?,
    val role: String = "PATIENT"
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    val user: UserResponse
)

data class UserResponse(
    val id: Int,
    val email: String,
    val username: String,
    @SerializedName("full_name") val fullName: String?,
    val role: String,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("is_verified") val isVerified: Boolean,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)

// ========== Profile Models ==========

data class PatientProfileResponse(
    val id: Int,
    val email: String,
    val username: String,
    @SerializedName("full_name") val fullName: String?,
    val role: String,
    val phone: String?,
    val address: String?,
    @SerializedName("linked_doctor_id") val linkedDoctorId: Int?,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)

data class PatientProfileUpdate(
    @SerializedName("full_name") val fullName: String? = null,
    val phone: String? = null,
    val address: String? = null
)

data class LinkDoctorRequest(
    @SerializedName("doctor_code") val doctorCode: String
)

data class DoctorCodeResponse(
    @SerializedName("doctor_id") val doctorId: Int,
    @SerializedName("doctor_code") val doctorCode: String,
    val message: String
)

data class LinkedDoctorResponse(
    @SerializedName("doctor_id") val doctorId: Int,
    val name: String,
    val email: String,
    val username: String,
    val phone: String?
)

data class MyPatientsResponse(
    @SerializedName("doctor_id") val doctorId: Int,
    @SerializedName("patient_count") val patientCount: Int,
    val patients: List<UserResponse>
)

// ========== Appointment Models ==========

data class DoctorAppointmentCreate(
    @SerializedName("doctor_id") val doctorId: Int,
    @SerializedName("appointment_date") val appointmentDate: String,
    val reason: String? = null,
    val notes: String? = null
)

data class DoctorAppointmentUpdate(
    @SerializedName("appointment_date") val appointmentDate: String? = null,
    val reason: String? = null,
    val notes: String? = null,
    val status: String? = null
)

data class DoctorAppointmentResponse(
    val id: Int,
    @SerializedName("patient_id") val patientId: Int,
    @SerializedName("doctor_id") val doctorId: Int,
    @SerializedName("appointment_date") val appointmentDate: String,
    val reason: String?,
    val notes: String?,
    val status: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)

data class LabAppointmentCreate(
    @SerializedName("lab_id") val labId: Int,
    @SerializedName("appointment_date") val appointmentDate: String,
    @SerializedName("test_type") val testType: String,
    val reason: String? = null,
    val notes: String? = null
)

data class DoctorCreateLabAppointment(
    @SerializedName("patient_id") val patientId: Int,
    @SerializedName("lab_id") val labId: Int,
    @SerializedName("appointment_date") val appointmentDate: String,
    @SerializedName("test_type") val testType: String,
    val reason: String? = null,
    val notes: String? = null
)

data class LabAppointmentUpdate(
    @SerializedName("appointment_date") val appointmentDate: String? = null,
    @SerializedName("test_type") val testType: String? = null,
    val reason: String? = null,
    val notes: String? = null,
    val status: String? = null
)

data class LabAppointmentResponse(
    val id: Int,
    @SerializedName("patient_id") val patientId: Int,
    @SerializedName("doctor_id") val doctorId: Int?,
    @SerializedName("lab_id") val labId: Int,
    @SerializedName("appointment_date") val appointmentDate: String,
    @SerializedName("test_type") val testType: String,
    val reason: String?,
    val notes: String?,
    val status: String,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)

// ========== Report Models ==========

data class LabReportResponse(
    val id: Int,
    @SerializedName("appointment_id") val appointmentId: Int,
    @SerializedName("uploaded_by_id") val uploadedById: Int,
    @SerializedName("file_name") val fileName: String,
    @SerializedName("file_size") val fileSize: Int,
    @SerializedName("mime_type") val mimeType: String,
    @SerializedName("test_results") val testResults: String?,
    val notes: String?,
    @SerializedName("ai_summary") val aiSummary: String?,
    @SerializedName("ai_key_findings") val aiKeyFindings: String?,
    @SerializedName("ai_abnormal_values") val aiAbnormalValues: String?,
    @SerializedName("ai_clinical_significance") val aiClinicalSignificance: String?,
    @SerializedName("ai_doctor_recommendation") val aiDoctorRecommendation: String?,
    @SerializedName("ai_analysis_status") val aiAnalysisStatus: String,
    @SerializedName("ai_analysis_error") val aiAnalysisError: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("updated_at") val updatedAt: String
)

// ========== Query Models ==========

data class QueryCreateRequest(
    @SerializedName("query_text") val queryText: String,
    val urgency: String = "MEDIUM"
)

data class QueryRespondRequest(
    @SerializedName("response_text") val responseText: String
)

data class QueryResponse(
    val id: Int,
    @SerializedName("patient_id") val patientId: Int,
    @SerializedName("doctor_id") val doctorId: Int,
    @SerializedName("query_text") val queryText: String,
    @SerializedName("response_text") val responseText: String?,
    val urgency: String,
    @SerializedName("is_responded") val isResponded: Boolean,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("responded_at") val respondedAt: String?
)

data class PendingCountResponse(
    @SerializedName("doctor_id") val doctorId: Int,
    @SerializedName("pending_count") val pendingCount: Int
)

// ========== Generic ==========

data class ErrorResponse(
    val detail: String
)

data class MessageResponse(
    val message: String
)

data class ProfileResponse(
    val role: String,
    val profile: Map<String, Any?>
)
