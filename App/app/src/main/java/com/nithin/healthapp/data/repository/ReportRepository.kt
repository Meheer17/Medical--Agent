package com.nithin.healthapp.data.repository

import android.content.Context
import com.nithin.healthapp.data.api.RetrofitClient
import com.nithin.healthapp.data.models.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.File

class ReportRepository(context: Context) {
    private val api = RetrofitClient.getApiService(context)

    suspend fun getMyReports(): Result<List<LabReportResponse>> {
        return try {
            val response = api.getMyReports()
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Failed to get reports"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getReport(appointmentId: Int): Result<LabReportResponse> {
        return try {
            val response = api.getLabReport(appointmentId)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception("Report not found"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun uploadReport(
        appointmentId: Int,
        file: File,
        testResults: String?,
        notes: String?
    ): Result<LabReportResponse> {
        return try {
            val requestFile = file.asRequestBody("application/pdf".toMediaTypeOrNull())
            val filePart = MultipartBody.Part.createFormData("file", file.name, requestFile)
            val testResultsBody = testResults?.toRequestBody("text/plain".toMediaTypeOrNull())
            val notesBody = notes?.toRequestBody("text/plain".toMediaTypeOrNull())

            val response = api.uploadLabReport(appointmentId, filePart, testResultsBody, notesBody)
            if (response.isSuccessful) Result.success(response.body()!!)
            else Result.failure(Exception(response.errorBody()?.string() ?: "Upload failed"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteReport(appointmentId: Int): Result<Unit> {
        return try {
            val response = api.deleteLabReport(appointmentId)
            if (response.isSuccessful) Result.success(Unit)
            else Result.failure(Exception("Failed to delete report"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun downloadReportFile(appointmentId: Int, cacheDir: File): Result<File> {
        return try {
            val response = api.downloadReportFile(appointmentId)
            if (response.isSuccessful) {
                val body = response.body() ?: return Result.failure(Exception("Empty response"))
                val file = File(cacheDir, "report_${appointmentId}.pdf")
                file.outputStream().use { output ->
                    body.byteStream().use { input ->
                        input.copyTo(output)
                    }
                }
                Result.success(file)
            } else {
                Result.failure(Exception("Failed to download report"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
