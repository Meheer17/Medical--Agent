package com.nithin.healthapp.ui.lab

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.nithin.healthapp.data.models.LabAppointmentUpdate
import com.nithin.healthapp.databinding.FragmentLabAppointmentsBinding
import com.nithin.healthapp.ui.common.AppointmentAdapter

class LabAppointmentsFragment : Fragment() {

    private var _binding: FragmentLabAppointmentsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: LabViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentLabAppointmentsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvAppointments.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { viewModel.loadAppointments() }

        viewModel.labAppointments.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { appointments ->
                if (appointments.isEmpty()) {
                    binding.tvNoAppointments.visibility = View.VISIBLE
                    binding.rvAppointments.visibility = View.GONE
                } else {
                    binding.tvNoAppointments.visibility = View.GONE
                    binding.rvAppointments.visibility = View.VISIBLE
                    val items = appointments.map { appt ->
                        AppointmentAdapter.AppointmentItem(
                            id = appt.id, title = appt.testType,
                            subtitle = "Patient #${appt.patientId} • ${appt.reason ?: "No reason"}",
                            date = appt.appointmentDate, status = appt.status, type = "LAB"
                        )
                    }
                    binding.rvAppointments.adapter = AppointmentAdapter(items) { item ->
                        showStatusUpdateDialog(item)
                    }
                }
            }
            result.onFailure {
                binding.tvNoAppointments.visibility = View.VISIBLE
                binding.rvAppointments.visibility = View.GONE
            }
        }

        viewModel.updateApptResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Status updated!", Toast.LENGTH_SHORT).show()
                viewModel.loadAppointments()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loadAppointments()
    }

    private fun showStatusUpdateDialog(item: AppointmentAdapter.AppointmentItem) {
        val statuses = arrayOf("CONFIRMED", "COMPLETED", "CANCELLED")
        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Update Status - ${item.title}")
            .setItems(statuses.map { it.replaceFirstChar { c -> c.uppercase() } }.toTypedArray()) { _, which ->
                viewModel.updateAppointment(item.id, LabAppointmentUpdate(status = statuses[which]))
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
