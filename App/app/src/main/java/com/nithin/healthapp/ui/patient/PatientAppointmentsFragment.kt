package com.nithin.healthapp.ui.patient

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
import com.nithin.healthapp.R
import com.nithin.healthapp.data.models.DoctorAppointmentCreate
import com.nithin.healthapp.data.models.LabAppointmentCreate
import com.nithin.healthapp.data.models.LinkedDoctorResponse
import com.nithin.healthapp.data.models.SimpleUserItem
import com.nithin.healthapp.databinding.FragmentPatientAppointmentsBinding
import com.nithin.healthapp.ui.common.AppointmentAdapter
import com.nithin.healthapp.util.DateUtils
import java.util.*

class PatientAppointmentsFragment : Fragment() {

    private var _binding: FragmentPatientAppointmentsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    private var cachedLinkedDoctor: LinkedDoctorResponse? = null
    private var cachedLabs: List<SimpleUserItem> = emptyList()

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
        viewModel.loadLinkedDoctor()
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

        viewModel.linkedDoctor.observe(viewLifecycleOwner) { result ->
            result.onSuccess { doctor -> cachedLinkedDoctor = doctor }
            result.onFailure { cachedLinkedDoctor = null }
        }

        viewModel.labs.observe(viewLifecycleOwner) { result ->
            result.onSuccess { labs -> cachedLabs = labs }
        }
    }

    private fun showCreateDoctorAppointmentDialog() {
        val doctor = cachedLinkedDoctor
        if (doctor == null) {
            Toast.makeText(requireContext(), "You must link to a doctor first. Go to Profile to link.", Toast.LENGTH_LONG).show()
            return
        }

        val dialogView = layoutInflater.inflate(R.layout.dialog_create_doctor_appointment, null)
        val etDoctorName = dialogView.findViewById<TextInputEditText>(R.id.et_doctor_name)
        val etDate = dialogView.findViewById<TextInputEditText>(R.id.et_date)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.et_reason)
        val etNotes = dialogView.findViewById<TextInputEditText>(R.id.et_notes)

        etDoctorName.setText(doctor.name)

        var selectedDate = ""
        etDate.setOnClickListener { pickDateTime { dateStr -> selectedDate = dateStr; etDate.setText(DateUtils.formatDisplayDateTime(dateStr)) } }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Book Doctor Appointment")
            .setView(dialogView)
            .setPositiveButton("Book") { _, _ ->
                if (selectedDate.isEmpty()) {
                    Toast.makeText(requireContext(), "Please select a date", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.createDoctorAppointment(
                    DoctorAppointmentCreate(doctor.doctorId, selectedDate, etReason.text?.toString(), etNotes.text?.toString())
                )
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showCreateLabAppointmentDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_create_lab_appointment, null)
        val actvLab = dialogView.findViewById<AutoCompleteTextView>(R.id.actv_lab)
        val etDate = dialogView.findViewById<TextInputEditText>(R.id.et_date)
        val actvTestType = dialogView.findViewById<AutoCompleteTextView>(R.id.actv_test_type)
        val etReason = dialogView.findViewById<TextInputEditText>(R.id.et_reason)

        val labNames = cachedLabs.map { it.name }
        actvLab.setAdapter(ArrayAdapter(requireContext(), R.layout.item_dropdown, labNames))
        var selectedLabId: Int? = null
        actvLab.setOnItemClickListener { _, _, position, _ -> selectedLabId = cachedLabs[position].id }

        // Test type dropdown
        val testTypes = listOf(
            "Complete Blood Count (CBC)",
            "Comprehensive Metabolic Panel (CMP)",
            "Urinalysis Report",
            "Lipid Profile",
            "Thyroid Function Test (Panel)"
        )
        actvTestType.setAdapter(ArrayAdapter(requireContext(), R.layout.item_dropdown, testTypes))
        var selectedTestType: String? = null
        actvTestType.setOnItemClickListener { _, _, position, _ -> selectedTestType = testTypes[position] }

        var selectedDate = ""
        etDate.setOnClickListener { pickDateTime { dateStr -> selectedDate = dateStr; etDate.setText(DateUtils.formatDisplayDateTime(dateStr)) } }

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Book Lab Appointment")
            .setView(dialogView)
            .setPositiveButton("Book") { _, _ ->
                val labId = selectedLabId
                val testType = selectedTestType
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
