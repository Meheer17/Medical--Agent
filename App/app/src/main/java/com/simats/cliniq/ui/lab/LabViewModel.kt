package com.simats.cliniq.ui.lab

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.simats.cliniq.data.models.*
import com.simats.cliniq.data.repository.*
import kotlinx.coroutines.launch
import java.io.File

class LabViewModel(application: Application) : AndroidViewModel(application) {

    private val appointmentRepo = AppointmentRepository(application)
    private val reportRepo = ReportRepository(application)

    private val _labAppointments = MutableLiveData<Result<List<LabAppointmentResponse>>>()
    val labAppointments: LiveData<Result<List<LabAppointmentResponse>>> = _labAppointments

    private val _reports = MutableLiveData<Result<List<LabReportResponse>>>()
    val reports: LiveData<Result<List<LabReportResponse>>> = _reports

    private val _uploadResult = MutableLiveData<Result<LabReportResponse>>()
    val uploadResult: LiveData<Result<LabReportResponse>> = _uploadResult

    private val _deleteResult = MutableLiveData<Result<Unit>>()
    val deleteResult: LiveData<Result<Unit>> = _deleteResult

    private val _updateApptResult = MutableLiveData<Result<LabAppointmentResponse>>()
    val updateApptResult: LiveData<Result<LabAppointmentResponse>> = _updateApptResult

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadAppointments() {
        viewModelScope.launch {
            _isLoading.value = true
            _labAppointments.value = appointmentRepo.getMyLabAppointments()
            _isLoading.value = false
        }
    }

    fun loadReports() {
        viewModelScope.launch {
            _isLoading.value = true
            _reports.value = reportRepo.getMyReports()
            _isLoading.value = false
        }
    }

    fun uploadReport(appointmentId: Int, file: File, testResults: String?, notes: String?) {
        viewModelScope.launch {
            _isLoading.value = true
            _uploadResult.value = reportRepo.uploadReport(appointmentId, file, testResults, notes)
            _isLoading.value = false
        }
    }

    fun deleteReport(appointmentId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _deleteResult.value = reportRepo.deleteReport(appointmentId)
            _isLoading.value = false
        }
    }

    fun updateAppointment(id: Int, update: LabAppointmentUpdate) {
        viewModelScope.launch {
            _isLoading.value = true
            _updateApptResult.value = appointmentRepo.updateLabAppointment(id, update)
            _isLoading.value = false
        }
    }

    // Download report
    private val _downloadedFile = MutableLiveData<Result<File>>()
    val downloadedFile: LiveData<Result<File>> = _downloadedFile

    fun downloadReport(appointmentId: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            _downloadedFile.value = reportRepo.downloadReportFile(
                appointmentId,
                getApplication<Application>().cacheDir
            )
            _isLoading.value = false
        }
    }
}
