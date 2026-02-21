package com.nithin.healthapp.ui.doctor

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.nithin.healthapp.R
import com.nithin.healthapp.data.models.DoctorAppointmentUpdate
import com.nithin.healthapp.data.models.DoctorCreateLabAppointment
import com.nithin.healthapp.databinding.FragmentDoctorAppointmentsBinding
import com.nithin.healthapp.ui.common.AppointmentAdapter
import com.nithin.healthapp.util.DateUtils
import java.util.*

class DoctorAppointmentsFragment : Fragment() {

    private var _binding: FragmentDoctorAppointmentsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

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
        val etPatientId = dialogView.findViewById<TextInputEditText>(R.id.et_patient_id)
        val etLabId = dialogView.findViewById<TextInputEditText>(R.id.et_lab_id)
        val etDate = dialogView.findViewById<TextInputEditText>(R.id.et_date)
        val etTestType = dialogView.findViewById<TextInputEditText>(R.id.et_test_type)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.et_reason)

        var selectedDate = ""
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
                val patientId = etPatientId.text.toString().toIntOrNull()
                val labId = etLabId.text.toString().toIntOrNull()
                val testType = etTestType.text?.toString()
                if (patientId == null || labId == null || selectedDate.isEmpty() || testType.isNullOrEmpty()) {
                    Toast.makeText(requireContext(), "Fill all required fields", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.createLabAppointmentForPatient(
                    DoctorCreateLabAppointment(patientId, labId, selectedDate, testType, etReason.text?.toString())
                )
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
