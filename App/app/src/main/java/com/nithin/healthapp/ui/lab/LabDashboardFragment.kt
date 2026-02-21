package com.nithin.healthapp.ui.lab

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.nithin.healthapp.databinding.FragmentLabDashboardBinding
import com.nithin.healthapp.ui.common.AppointmentAdapter

class LabDashboardFragment : Fragment() {

    private var _binding: FragmentLabDashboardBinding? = null
    private val binding get() = _binding!!
    private val viewModel: LabViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentLabDashboardBinding.inflate(inflater, container, false)
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
        viewModel.loadAppointments()
        viewModel.loadReports()
    }

    private fun observeData() {
        viewModel.labAppointments.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { appointments ->
                val upcoming = appointments.filter { it.status == "SCHEDULED" || it.status == "CONFIRMED" }
                binding.tvAppointmentCount.text = "${upcoming.size}"
                binding.tvTotalAppointments.text = "Total: ${appointments.size}"

                val adapter = AppointmentAdapter(upcoming.take(5).map { appt ->
                    AppointmentAdapter.AppointmentItem(
                        id = appt.id,
                        title = appt.testType,
                        subtitle = "Patient #${appt.patientId}",
                        date = appt.appointmentDate,
                        status = appt.status,
                        type = "LABb"
                    )
                })
                binding.rvUpcomingAppointments.adapter = adapter
            }
            result.onFailure { binding.tvAppointmentCount.text = "0" }
        }

        viewModel.reports.observe(viewLifecycleOwner) { result ->
            result.onSuccess { binding.tvReportCount.text = "${it.size}" }
            result.onFailure { binding.tvReportCount.text = "0" }
        }
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
