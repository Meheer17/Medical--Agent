package com.simats.cliniq.ui.doctor

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.simats.cliniq.databinding.FragmentDoctorDashboardBinding
import com.simats.cliniq.ui.common.AppointmentAdapter

class DoctorDashboardFragment : Fragment() {

    private var _binding: FragmentDoctorDashboardBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDoctorDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvUpcomingAppointments.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { loadData() }

        observeData()
        loadData()
    }

    private fun loadData() {
        viewModel.loadDoctorAppointments()
        viewModel.loadPendingCount()
        viewModel.loadPatients()
        viewModel.loadReports()
    }

    private fun observeData() {
        viewModel.doctorAppointments.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { appointments ->
                val upcoming = appointments.filter { it.status == "SCHEDULED" || it.status == "CONFIRMED" }
                binding.tvAppointmentCount.text = "${upcoming.size}"

                val adapter = AppointmentAdapter(upcoming.take(5).map { appt ->
                    AppointmentAdapter.AppointmentItem(
                        id = appt.id,
                        title = "Patient #${appt.patientId}",
                        subtitle = appt.reason ?: "Consultation",
                        date = appt.appointmentDate,
                        status = appt.status,
                        type = "DOCTOR"
                    )
                })
                binding.rvUpcomingAppointments.adapter = adapter
            }
            result.onFailure { binding.tvAppointmentCount.text = "0" }
        }

        viewModel.pendingCount.observe(viewLifecycleOwner) { result ->
            result.onSuccess { binding.tvPendingQueries.text = "${it.pendingCount}" }
            result.onFailure { binding.tvPendingQueries.text = "0" }
        }

        viewModel.patients.observe(viewLifecycleOwner) { result ->
            result.onSuccess { binding.tvPatientCount.text = "${it.patientCount}" }
            result.onFailure { binding.tvPatientCount.text = "0" }
        }

        viewModel.reports.observe(viewLifecycleOwner) { result ->
            result.onSuccess { binding.tvReportCount.text = "${it.size}" }
            result.onFailure { binding.tvReportCount.text = "0" }
        }
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
