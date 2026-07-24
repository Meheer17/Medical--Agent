package com.simats.cliniq.ui.doctor

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.simats.cliniq.R
import com.simats.cliniq.data.models.DoctorAppointmentUpdate
import com.simats.cliniq.data.models.DoctorCreateLabAppointment
import com.simats.cliniq.data.models.SimpleUserItem
import com.simats.cliniq.data.models.UserResponse
import com.simats.cliniq.databinding.FragmentDoctorAppointmentsBinding
import com.simats.cliniq.ui.common.AppointmentAdapter
import com.simats.cliniq.util.DateUtils
import java.util.*

class DoctorAppointmentsFragment : Fragment() {

    private var _binding: FragmentDoctorAppointmentsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

    private var cachedPatients: List<UserResponse> = emptyList()
    private var cachedLabs: List<SimpleUserItem> = emptyList()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDoctorAppointmentsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvDoctorAppointments.layoutManager = LinearLayoutManager(requireContext())
        binding.rvLabAppointments.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadDoctorAppointments()
            viewModel.loadLabAppointments()
        }

        binding.fabCreateLabAppt.setOnClickListener { showCreateLabAppointmentDialog() }

        observeData()
        viewModel.loadDoctorAppointments()
        viewModel.loadLabAppointments()
        viewModel.loadPatients()
        viewModel.loadLabs()
    }

    private fun observeData() {
        viewModel.doctorAppointments.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { appointments ->
                if (appointments.isEmpty()) {
                    binding.tvNoDoctorAppts.visibility = View.VISIBLE
                    binding.rvDoctorAppointments.visibility = View.GONE
                } else {
                    binding.tvNoDoctorAppts.visibility = View.GONE
                    binding.rvDoctorAppointments.visibility = View.VISIBLE
                    val items = appointments.map { appt ->
                        AppointmentAdapter.AppointmentItem(
                            id = appt.id, title = "Patient #${appt.patientId}",
                            subtitle = appt.reason ?: "Consultation",
                            date = appt.appointmentDate, status = appt.status, type = "DOCTOR"
                        )
                    }
                    binding.rvDoctorAppointments.adapter = AppointmentAdapter(items) { item ->
                        showUpdateDialog(item)
                    }
                }
            }
        }

        viewModel.labAppointments.observe(viewLifecycleOwner) { result ->
            result.onSuccess { appointments ->
                if (appointments.isEmpty()) {
                    binding.tvNoLabAppts.visibility = View.VISIBLE
                    binding.rvLabAppointments.visibility = View.GONE
                } else {
                    binding.tvNoLabAppts.visibility = View.GONE
                    binding.rvLabAppointments.visibility = View.VISIBLE
                    val items = appointments.map { appt ->
                        AppointmentAdapter.AppointmentItem(
                            id = appt.id, title = appt.testType,
                            subtitle = "Patient #${appt.patientId}",
                            date = appt.appointmentDate, status = appt.status, type = "LAB"
                        )
                    }
                    binding.rvLabAppointments.adapter = AppointmentAdapter(items)
                }
            }
        }

        viewModel.updateResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Appointment updated!", Toast.LENGTH_SHORT).show()
                viewModel.loadDoctorAppointments()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.createLabAppt.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Lab appointment created!", Toast.LENGTH_SHORT).show()
                viewModel.loadLabAppointments()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.patients.observe(viewLifecycleOwner) { result ->
            result.onSuccess { data ->
                cachedPatients = data.patients
            }
        }

        viewModel.labs.observe(viewLifecycleOwner) { result ->
            result.onSuccess { labs ->
                cachedLabs = labs
            }
        }
    }

    private fun showUpdateDialog(item: AppointmentAdapter.AppointmentItem) {
        val statuses = arrayOf("CONFIRMED", "COMPLETED", "CANCELLED")
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Update Appointment #${item.id}")
            .setItems(statuses.map { it.replaceFirstChar { c -> c.uppercase() } }.toTypedArray()) { _, which ->
                viewModel.updateDoctorAppointment(item.id, DoctorAppointmentUpdate(status = statuses[which]))
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showCreateLabAppointmentDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_doctor_create_lab_appt, null)
        val actvPatient = dialogView.findViewById<AutoCompleteTextView>(R.id.actv_patient)
        val actvLab = dialogView.findViewById<AutoCompleteTextView>(R.id.actv_lab)
        val etDate = dialogView.findViewById<TextInputEditText>(R.id.et_date)
        val actvTestType = dialogView.findViewById<AutoCompleteTextView>(R.id.actv_test_type)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.et_reason)

        var selectedPatientId: Int? = null
        var selectedLabId: Int? = null
        var selectedDate = ""

        // Populate patient dropdown
        val patientNames = cachedPatients.map { it.fullName ?: it.username }
        val patientAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, patientNames)
        actvPatient.setAdapter(patientAdapter)
        actvPatient.setOnItemClickListener { _, _, position, _ ->
            selectedPatientId = cachedPatients[position].id
        }

        // Populate lab dropdown
        val labNames = cachedLabs.map { it.name }
        val labAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, labNames)
        actvLab.setAdapter(labAdapter)
        actvLab.setOnItemClickListener { _, _, position, _ ->
            selectedLabId = cachedLabs[position].id
        }

        // Test type dropdown
        val testTypes = listOf(
            "Complete Blood Count (CBC)",
            "Comprehensive Metabolic Panel (CMP)",
            "Urinalysis Report",
            "Lipid Profile",
            "Thyroid Function Test (Panel)"
        )
        val testTypeAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, testTypes)
        actvTestType.setAdapter(testTypeAdapter)
        var selectedTestType: String? = null
        actvTestType.setOnItemClickListener { _, _, position, _ ->
            selectedTestType = testTypes[position]
        }

        etDate.setOnClickListener {
            val cal = Calendar.getInstance()
            DatePickerDialog(requireContext(), { _, y, m, d ->
                TimePickerDialog(requireContext(), { _, h, min ->
                    selectedDate = DateUtils.formatForApi(y, m, d, h, min)
                    etDate.setText(DateUtils.formatDisplayDateTime(selectedDate))
                }, cal.get(Calendar.HOUR_OF_DAY), cal.get(Calendar.MINUTE), false).show()
            }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
        }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Create Lab Appointment for Patient")
            .setView(dialogView)
            .setPositiveButton("Create") { _, _ ->
                val testType = selectedTestType
                if (selectedPatientId == null || selectedLabId == null || selectedDate.isEmpty() || testType.isNullOrEmpty()) {
                    Toast.makeText(requireContext(), "Fill all required fields", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.createLabAppointmentForPatient(
                    DoctorCreateLabAppointment(selectedPatientId!!, selectedLabId!!, selectedDate, testType, etReason.text?.toString())
                )
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
