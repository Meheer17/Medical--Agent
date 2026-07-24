package com.simats.cliniq.ui.patient

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.simats.cliniq.databinding.FragmentPatientDashboardBinding
import com.simats.cliniq.ui.common.AppointmentAdapter

class PatientDashboardFragment : Fragment() {

    private var _binding: FragmentPatientDashboardBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentPatientDashboardBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvUpcomingAppointments.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener {
            loadData()
        }

        observeData()
        loadData()
    }

    private fun loadData() {
        viewModel.loadDoctorAppointments()
        viewModel.loadLabAppointments()
        viewModel.loadReports()
        viewModel.loadLinkedDoctor()
    }

    private fun observeData() {
        viewModel.doctorAppointments.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { appointments ->
                val upcoming = appointments.filter { it.status == "SCHEDULED" || it.status == "CONFIRMED" }
                binding.tvAppointmentCount.text = "${upcoming.size}"
                binding.tvAppointmentLabel.text = "Upcoming Doctor Appointments"

                val adapter = AppointmentAdapter(upcoming.take(3).map { appt ->
                    AppointmentAdapter.AppointmentItem(
                        id = appt.id,
                        title = "Doctor Appointment #${appt.id}",
                        subtitle = appt.reason ?: "General consultation",
                        date = appt.appointmentDate,
                        status = appt.status,
                        type = "DOCTOR"
                    )
                })
                binding.rvUpcomingAppointments.adapter = adapter
            }
            result.onFailure {
                binding.tvAppointmentCount.text = "0"
            }
        }

        viewModel.labAppointments.observe(viewLifecycleOwner) { result ->
            result.onSuccess { appointments ->
                val upcoming = appointments.filter { it.status == "SCHEDULED" || it.status == "CONFIRMED" }
                binding.tvLabAppointmentCount.text = "${upcoming.size}"
            }
            result.onFailure {
                binding.tvLabAppointmentCount.text = "0"
            }
        }

        viewModel.reports.observe(viewLifecycleOwner) { result ->
            result.onSuccess { reports ->
                binding.tvReportCount.text = "${reports.size}"
            }
            result.onFailure {
                binding.tvReportCount.text = "0"
            }
        }

        viewModel.linkedDoctor.observe(viewLifecycleOwner) { result ->
            result.onSuccess { doctor ->
                binding.tvLinkedDoctor.text = doctor.name
                binding.tvLinkedDoctorLabel.text = "Linked Doctor"
            }
            result.onFailure {
                binding.tvLinkedDoctor.text = "Not linked"
                binding.tvLinkedDoctorLabel.text = "Link to a doctor in Profile"
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
