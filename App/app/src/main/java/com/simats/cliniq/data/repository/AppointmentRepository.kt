package com.simats.cliniq.data.repository

import android.content.Context
import com.simats.cliniq.data.api.RetrofitClient
import com.simats.cliniq.data.models.*

class AppointmentRepository(context: Context) {
    private val api = RetrofitClient.getApiService(context)

    // ===== Doctor Appointments =====

    suspend fun createDoctorAppointment(appointment: DoctorAppointmentCreate): Result<DoctorAppointmentResponse> {
        return try {
            val response = api.createDoctorAppointment(appointment)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to create appointment"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMyDoctorAppointments(): Result<List<DoctorAppointmentResponse>> {
        return try {
            val response = api.getMyDoctorAppointments()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to fetch appointments"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateDoctorAppointment(id: Int, update: DoctorAppointmentUpdate): Result<DoctorAppointmentResponse> {
        return try {
            val response = api.updateDoctorAppointment(id, update)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to update"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun cancelDoctorAppointment(id: Int): Result<Unit> {
        return try {
            val response = api.cancelDoctorAppointment(id)
            if (response.isSuccessful) Result.success(Unit)
            else Result.failure(Exception("Failed to cancel appointment"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ===== Lab Appointments =====

    suspend fun createLabAppointment(appointment: LabAppointmentCreate): Result<LabAppointmentResponse> {
        return try {
            val response = api.createLabAppointment(appointment)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to create"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun doctorCreateLabAppointment(appointment: DoctorCreateLabAppointment): Result<LabAppointmentResponse> {
        return try {
            val response = api.doctorCreateLabAppointment(appointment)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to create"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getMyLabAppointments(): Result<List<LabAppointmentResponse>> {
        return try {
            val response = api.getMyLabAppointments()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to fetch lab appointments"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateLabAppointment(id: Int, update: LabAppointmentUpdate): Result<LabAppointmentResponse> {
        return try {
            val response = api.updateLabAppointment(id, update)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Failed to update"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
