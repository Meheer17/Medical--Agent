package com.nithin.healthapp.ui.patient

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
import com.nithin.healthapp.data.models.DoctorAppointmentCreate
import com.nithin.healthapp.data.models.LabAppointmentCreate
import com.nithin.healthapp.databinding.FragmentPatientAppointmentsBinding
import com.nithin.healthapp.ui.common.AppointmentAdapter
import com.nithin.healthapp.util.DateUtils
import java.util.*

class PatientAppointmentsFragment : Fragment() {

    private var _binding: FragmentPatientAppointmentsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentPatientAppointmentsBinding.inflate(inflater, container, false)
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

        binding.fabCreateDoctorAppt.setOnClickListener { showCreateDoctorAppointmentDialog() }
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
                            id = appt.id, title = "Doctor Appt #${appt.id}",
                            subtitle = appt.reason ?: "General consultation",
                            date = appt.appointmentDate, status = appt.status, type = "DOCTOR"
                        )
                    }
                    binding.rvDoctorAppointments.adapter = AppointmentAdapter(items) { item ->
                        if (item.status == "SCHEDULED" || item.status == "CONFIRMED") {
                            MaterialAlertDialogBuilder(requireContext())
                                .setTitle("Cancel Appointment")
                                .setMessage("Cancel appointment #${item.id}?")
                                .setPositiveButton("Cancel It") { _, _ -> viewModel.cancelDoctorAppointment(item.id) }
                                .setNegativeButton("Keep", null)
                                .show()
                        }
                    }
                }
            }
            result.onFailure {
                binding.tvNoDoctorAppts.visibility = View.VISIBLE
                binding.rvDoctorAppointments.visibility = View.GONE
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
                            subtitle = appt.reason ?: "Lab test",
                            date = appt.appointmentDate, status = appt.status, type = "LAB"
                        )
                    }
                    binding.rvLabAppointments.adapter = AppointmentAdapter(items)
                }
            }
            result.onFailure {
                binding.tvNoLabAppts.visibility = View.VISIBLE
                binding.rvLabAppointments.visibility = View.GONE
            }
        }

        viewModel.createResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Appointment created!", Toast.LENGTH_SHORT).show()
                viewModel.loadDoctorAppointments()
                viewModel.loadLabAppointments()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun showCreateDoctorAppointmentDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_create_doctor_appointment, null)
        val etDoctorId = dialogView.findViewById<TextInputEditText>(R.id.et_doctor_id)
        val etDate = dialogView.findViewById<TextInputEditText>(R.id.et_date)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.et_reason)
        val etNotes = dialogView.findViewById<TextInputEditText>(R.id.et_notes)

        var selectedDate = ""
        etDate.setOnClickListener { pickDateTime { dateStr -> selectedDate = dateStr; etDate.setText(DateUtils.formatDisplayDateTime(dateStr)) } }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Book Doctor Appointment")
            .setView(dialogView)
            .setPositiveButton("Book") { _, _ ->
                val doctorId = etDoctorId.text.toString().toIntOrNull()
                if (doctorId == null || selectedDate.isEmpty()) {
                    Toast.makeText(requireContext(), "Please fill required fields", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.createDoctorAppointment(
                    DoctorAppointmentCreate(doctorId, selectedDate, etReason.text?.toString(), etNotes.text?.toString())
                )
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showCreateLabAppointmentDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_create_lab_appointment, null)
        val etLabId = dialogView.findViewById<TextInputEditText>(R.id.et_lab_id)
        val etDate = dialogView.findViewById<TextInputEditText>(R.id.et_date)
        val etTestType = dialogView.findViewById<TextInputEditText>(R.id.et_test_type)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.et_reason)

        var selectedDate = ""
        etDate.setOnClickListener { pickDateTime { dateStr -> selectedDate = dateStr; etDate.setText(DateUtils.formatDisplayDateTime(dateStr)) } }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Book Lab Appointment")
            .setView(dialogView)
            .setPositiveButton("Book") { _, _ ->
                val labId = etLabId.text.toString().toIntOrNull()
                val testType = etTestType.text?.toString()
                if (labId == null || selectedDate.isEmpty() || testType.isNullOrEmpty()) {
                    Toast.makeText(requireContext(), "Please fill required fields", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.createLabAppointment(
                    LabAppointmentCreate(labId, selectedDate, testType, etReason.text?.toString())
                )
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun pickDateTime(callback: (String) -> Unit) {
        val cal = Calendar.getInstance()
        DatePickerDialog(requireContext(), { _, year, month, day ->
            TimePickerDialog(requireContext(), { _, hour, minute ->
                callback(DateUtils.formatForApi(year, month, day, hour, minute))
            }, cal.get(Calendar.HOUR_OF_DAY), cal.get(Calendar.MINUTE), false).show()
        }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
