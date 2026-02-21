package com.nithin.healthapp.ui.patient

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.nithin.healthapp.data.models.*
import com.nithin.healthapp.data.repository.*
import kotlinx.coroutines.launch

class PatientViewModel(application: Application) : AndroidViewModel(application) {

    private val appointmentRepo = AppointmentRepository(application)
    private val reportRepo = ReportRepository(application)
    private val profileRepo = ProfileRepository(application)
    private val queryRepo = QueryRepository(application)

    // Doctor appointments
    private val _doctorAppointments = MutableLiveData<Result<List<DoctorAppointmentResponse>>>()
    val doctorAppointments: LiveData<Result<List<DoctorAppointmentResponse>>> = _doctorAppointments

    // Lab appointments
    private val _labAppointments = MutableLiveData<Result<List<LabAppointmentResponse>>>()
    val labAppointments: LiveData<Result<List<LabAppointmentResponse>>> = _labAppointments

    // Reports
    private val _reports = MutableLiveData<Result<List<LabReportResponse>>>()
    val reports: LiveData<Result<List<LabReportResponse>>> = _reports

    // Profile
    private val _profile = MutableLiveData<Result<PatientProfileResponse>>()
    val profile: LiveData<Result<PatientProfileResponse>> = _profile

    // Linked doctor
    private val _linkedDoctor = MutableLiveData<Result<LinkedDoctorResponse>>()
    val linkedDoctor: LiveData<Result<LinkedDoctorResponse>> = _linkedDoctor

    // Queries
    private val _queries = MutableLiveData<Result<List<QueryResponse>>>()
    val queries: LiveData<Result<List<QueryResponse>>> = _queries

    // Create appointment result
    private val _createResult = MutableLiveData<Result<Any>>()
    val createResult: LiveData<Result<Any>> = _createResult

    // Profile update
    private val _profileUpdate = MutableLiveData<Result<PatientProfileResponse>>()
    val profileUpdate: LiveData<Result<PatientProfileResponse>> = _profileUpdate

    // Link doctor
    private val _linkResult = MutableLiveData<Result<PatientProfileResponse>>()
    val linkResult: LiveData<Result<PatientProfileResponse>> = _linkResult

    // Query create
    private val _queryCreate = MutableLiveData<Result<QueryResponse>>()
    val queryCreate: LiveData<Result<QueryResponse>> = _queryCreate

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

    fun loadProfile() {
        viewModelScope.launch {
            _isLoading.value = true
            _profile.value = profileRepo.getMyProfile()
            _isLoading.value = false
        }
    }

    fun loadLinkedDoctor() {
        viewModelScope.launch {
            _linkedDoctor.value = profileRepo.getLinkedDoctor()
        }
    }

    fun loadQueries() {
        viewModelScope.launch {
            _isLoading.value = true
            _queries.value = queryRepo.getMyQueries()
            _isLoading.value = false
        }
    }

    fun createDoctorAppointment(appointment: DoctorAppointmentCreate) {
        viewModelScope.launch {
            _isLoading.value = true
            _createResult.value = appointmentRepo.createDoctorAppointment(appointment)
            _isLoading.value = false
        }
    }

    fun createLabAppointment(appointment: LabAppointmentCreate) {
        viewModelScope.launch {
            _isLoading.value = true
            _createResult.value = appointmentRepo.createLabAppointment(appointment)
            _isLoading.value = false
        }
    }

    fun cancelDoctorAppointment(id: Int) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = appointmentRepo.cancelDoctorAppointment(id)
            if (result.isSuccess) loadDoctorAppointments()
            _isLoading.value = false
        }
    }

    fun updateProfile(update: PatientProfileUpdate) {
        viewModelScope.launch {
            _isLoading.value = true
            _profileUpdate.value = profileRepo.updateProfile(update)
            _isLoading.value = false
        }
    }

    fun linkToDoctor(code: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _linkResult.value = profileRepo.linkToDoctor(code)
            _isLoading.value = false
        }
    }

    fun unlinkDoctor() {
        viewModelScope.launch {
            _isLoading.value = true
            profileRepo.unlinkDoctor()
            loadProfile()
            _isLoading.value = false
        }
    }

    fun createQuery(text: String, urgency: String) {
        viewModelScope.launch {
            _isLoading.value = true
            _queryCreate.value = queryRepo.createQuery(text, urgency)
            _isLoading.value = false
        }
    }
}
