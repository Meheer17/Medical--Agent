package com.nithin.healthapp.data.api

import com.nithin.healthapp.data.models.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // ==================== AUTH ====================

    @POST("api/auth/signup")
    suspend fun signup(@Body request: SignupRequest): Response<UserResponse>

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>

    @GET("api/auth/profile")
    suspend fun getProfile(): Response<ProfileResponse>

    // ==================== USER ====================

    @GET("api/users/me")
    suspend fun getCurrentUser(): Response<UserResponse>

    // ==================== PROFILES ====================

    @GET("api/profiles/me")
    suspend fun getMyProfile(): Response<PatientProfileResponse>

    @PUT("api/profiles/me")
    suspend fun updateMyProfile(@Body update: PatientProfileUpdate): Response<PatientProfileResponse>

    @POST("api/profiles/link-doctor")
    suspend fun linkToDoctor(@Body request: LinkDoctorRequest): Response<PatientProfileResponse>

    @POST("api/profiles/unlink-doctor")
    suspend fun unlinkFromDoctor(): Response<MessageResponse>

    @GET("api/profiles/my-code")
    suspend fun getMyDoctorCode(): Response<DoctorCodeResponse>

    @GET("api/profiles/regenerate-code")
    suspend fun regenerateDoctorCode(): Response<DoctorCodeResponse>

    @GET("api/profiles/my-patients")
    suspend fun getMyPatients(): Response<MyPatientsResponse>

    @GET("api/profiles/patient/{patient_id}")
    suspend fun getPatientById(@Path("patient_id") patientId: Int): Response<UserResponse>

    @GET("api/profiles/my-linked-doctor")
    suspend fun getMyLinkedDoctor(): Response<LinkedDoctorResponse>

    // ==================== DOCTOR APPOINTMENTS ====================

    @POST("api/appointments/doctor")
    suspend fun createDoctorAppointment(@Body appointment: DoctorAppointmentCreate): Response<DoctorAppointmentResponse>

    @GET("api/appointments/doctor/my-appointments")
    suspend fun getMyDoctorAppointments(): Response<List<DoctorAppointmentResponse>>

    @GET("api/appointments/doctor/{appointment_id}")
    suspend fun getDoctorAppointment(@Path("appointment_id") id: Int): Response<DoctorAppointmentResponse>

    @PUT("api/appointments/doctor/{appointment_id}")
    suspend fun updateDoctorAppointment(
        @Path("appointment_id") id: Int,
        @Body update: DoctorAppointmentUpdate
    ): Response<DoctorAppointmentResponse>

    @DELETE("api/appointments/doctor/{appointment_id}")
    suspend fun cancelDoctorAppointment(@Path("appointment_id") id: Int): Response<Unit>

    // ==================== LAB APPOINTMENTS ====================

    @POST("api/appointments/lab")
    suspend fun createLabAppointment(@Body appointment: LabAppointmentCreate): Response<LabAppointmentResponse>

    @POST("api/appointments/lab/doctor-create")
    suspend fun doctorCreateLabAppointment(@Body appointment: DoctorCreateLabAppointment): Response<LabAppointmentResponse>

    @GET("api/appointments/lab/my-appointments")
    suspend fun getMyLabAppointments(): Response<List<LabAppointmentResponse>>

    @GET("api/appointments/lab/{appointment_id}")
    suspend fun getLabAppointment(@Path("appointment_id") id: Int): Response<LabAppointmentResponse>

    @PUT("api/appointments/lab/{appointment_id}")
    suspend fun updateLabAppointment(
        @Path("appointment_id") id: Int,
        @Body update: LabAppointmentUpdate
    ): Response<LabAppointmentResponse>

    // ==================== LAB REPORTS ====================

    @Multipart
    @POST("api/reports/lab/{appointment_id}")
    suspend fun uploadLabReport(
        @Path("appointment_id") appointmentId: Int,
        @Part file: MultipartBody.Part,
        @Part("test_results") testResults: RequestBody?,
        @Part("notes") notes: RequestBody?
    ): Response<LabReportResponse>

    @GET("api/reports/lab/{appointment_id}")
    suspend fun getLabReport(@Path("appointment_id") appointmentId: Int): Response<LabReportResponse>

    @GET("api/reports/my-reports")
    suspend fun getMyReports(): Response<List<LabReportResponse>>

    @DELETE("api/reports/lab/{appointment_id}")
    suspend fun deleteLabReport(@Path("appointment_id") appointmentId: Int): Response<Unit>

    // ==================== QUERIES ====================

    @POST("api/queries")
    suspend fun createQuery(@Body query: QueryCreateRequest): Response<QueryResponse>

    @GET("api/queries")
    suspend fun getMyQueries(): Response<List<QueryResponse>>

    @GET("api/queries/{query_id}")
    suspend fun getQuery(@Path("query_id") id: Int): Response<QueryResponse>

    @POST("api/queries/{query_id}/respond")
    suspend fun respondToQuery(
        @Path("query_id") id: Int,
        @Body response: QueryRespondRequest
    ): Response<QueryResponse>

    @GET("api/queries/pending/count")
    suspend fun getPendingQueryCount(): Response<PendingCountResponse>

    @GET("api/queries/pending/list")
    suspend fun getPendingQueries(): Response<List<QueryResponse>>

    // ==================== HEALTH ====================

    @GET("health")
    suspend fun healthCheck(): Response<Map<String, String>>
}
