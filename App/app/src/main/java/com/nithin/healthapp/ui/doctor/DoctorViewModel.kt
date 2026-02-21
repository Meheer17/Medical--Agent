package com.nithin.healthapp.ui.doctor

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.nithin.healthapp.data.models.*
import com.nithin.healthapp.data.repository.*
import kotlinx.coroutines.launch

class DoctorViewModel(application: Application) : AndroidViewModel(application) {

    private val appointmentRepo = AppointmentRepository(application)
    private val profileRepo = ProfileRepository(application)
    private val queryRepo = QueryRepository(application)
    private val reportRepo = ReportRepository(application)

    private val _doctorAppointments = MutableLiveData<Result<List<DoctorAppointmentResponse>>>()
    val doctorAppointments: LiveData<Result<List<DoctorAppointmentResponse>>> = _doctorAppointments

    private val _labAppointments = MutableLiveData<Result<List<LabAppointmentResponse>>>()
    val labAppointments: LiveData<Result<List<LabAppointmentResponse>>> = _labAppointments

    private val _patients = MutableLiveData<Result<MyPatientsResponse>>()
    val patients: LiveData<Result<MyPatientsResponse>> = _patients

    private val _doctorCode = MutableLiveData<Result<DoctorCodeResponse>>()
    val doctorCode: LiveData<Result<DoctorCodeResponse>> = _doctorCode

    private val _queries = MutableLiveData<Result<List<QueryResponse>>>()
    val queries: LiveData<Result<List<QueryResponse>>> = _queries

    private val _pendingCount = MutableLiveData<Result<PendingCountResponse>>()
    val pendingCount: LiveData<Result<PendingCountResponse>> = _pendingCount

    private val _reports = MutableLiveData<Result<List<LabReportResponse>>>()
    val reports: LiveData<Result<List<LabReportResponse>>> = _reports

    private val _respondResult = MutableLiveData<Result<QueryResponse>>()
    val respondResult: LiveData<Result<QueryResponse>> = _respondResult

    private val _createLabAppt = MutableLiveData<Result<LabAppointmentResponse>>()
    val createLabAppt: LiveData<Result<LabAppointmentResponse>> = _createLabAppt

    private val _updateResult = MutableLiveData<Result<DoctorAppointmentResponse>>()
    val updateResult: LiveData<Result<DoctorAppointmentResponse>> = _updateResult

    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadDoctorAppointments() {
        viewModelScope.launch {
            _isLoading.value = true
            _doctorAppointments.value = appointmentRepo.getMyDoctorAppointments()
            _isLoading.value = false
        }
    }

    fun loadLabAppointments() {
        viewModelScope.launch {
            _labAppointments.value = appointmentRepo.getMyLabAppointments()
        }
    }

    fun loadPatients() {
        viewModelScope.launch {
            _isLoading.value = true
            _patients.value = profileRepo.getMyPatients()
            _isLoading.value = false
        }
    }

    fun loadDoctorCode() {
        viewModelScope.launch {
            _doctorCode.value = profileRepo.getDoctorCode()
        }
    }

    fun regenerateCode() {
        viewModelScope.launch {
            _isLoading.value = true
            _doctorCode.value = profileRepo.regenerateDoctorCode()
            _isLoading.value = false
        }
    }

    fun loadQueries() {
        viewModelScope.launch {
            _isLoading.value = true
            _queries.value = queryRepo.getMyQueries()
            _isLoading.value = false
        }
    }

    fun loadPendingCount() {
        viewModelScope.launch {
            _pendingCount.value = queryRepo.getPendingCount()
        }
    }

    fun loadReports() {
        viewModelScope.launch {
            _reports.value = reportRepo.getMyReports()
        }
    }

    fun respondToQuery(queryId: Int, responseText: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _respondResult.value = queryRepo.respondToQuery(queryId, responseText)
            _isLoading.value = false
        }
    }

    fun updateDoctorAppointment(id: Int, update: DoctorAppointmentUpdate) {
        viewModelScope.launch {
            _isLoading.value = true
            _updateResult.value = appointmentRepo.updateDoctorAppointment(id, update)
            _isLoading.value = false
        }
    }

    fun createLabAppointmentForPatient(appointment: DoctorCreateLabAppointment) {
        viewModelScope.launch {
            _isLoading.value = true
            _createLabAppt.value = appointmentRepo.doctorCreateLabAppointment(appointment)
            _isLoading.value = false
        }
    }
}
