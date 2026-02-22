package com.simats.cliniq.data.repository

import android.content.Context
import com.simats.cliniq.data.api.RetrofitClient
import com.simats.cliniq.data.models.*

class ProfileRepository(context: Context) {
    private val api = RetrofitClient.getApiService(context)

    suspend fun getMyProfile(): Result<PatientProfileResponse> {
        return try {
            val response = api.getMyProfile()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get profile"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateProfile(update: PatientProfileUpdate): Result<PatientProfileResponse> {
        return try {
            val response = api.updateMyProfile(update)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to update"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun linkToDoctor(doctorCode: String): Result<PatientProfileResponse> {
        return try {
            val response = api.linkToDoctor(LinkDoctorRequest(doctorCode))
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to link"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun unlinkDoctor(): Result<MessageResponse> {
        return try {
            val response = api.unlinkFromDoctor()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to unlink"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getLinkedDoctor(): Result<LinkedDoctorResponse> {
        return try {
            val response = api.getMyLinkedDoctor()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("No linked doctor"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getDoctorCode(): Result<DoctorCodeResponse> {
        return try {
            val response = api.getMyDoctorCode()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get code"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun regenerateDoctorCode(): Result<DoctorCodeResponse> {
        return try {
            val response = api.regenerateDoctorCode()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to regenerate"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMyPatients(): Result<MyPatientsResponse> {
        return try {
            val response = api.getMyPatients()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get patients"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPatientById(id: Int): Result<UserResponse> {
        return try {
            val response = api.getPatientById(id)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Patient not found"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun listAllDoctors(): Result<List<SimpleUserItem>> {
        return try {
            val response = api.listAllDoctors()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to list doctors"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun listAllLabs(): Result<List<SimpleUserItem>> {
        return try {
            val response = api.listAllLabs()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to list labs"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPatientReports(patientId: Int): Result<List<LabReportResponse>> {
        return try {
            val response = api.getPatientReports(patientId)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get patient reports"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPatientDoctorAppointments(patientId: Int): Result<List<DoctorAppointmentResponse>> {
        return try {
            val response = api.getPatientDoctorAppointments(patientId)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get patient appointments"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getPatientLabAppointments(patientId: Int): Result<List<LabAppointmentResponse>> {
        return try {
            val response = api.getPatientLabAppointments(patientId)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get patient lab appointments"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
