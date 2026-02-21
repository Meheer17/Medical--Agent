package com.nithin.healthapp.ui.doctor

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.content.FileProvider
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.nithin.healthapp.R
import com.nithin.healthapp.databinding.FragmentPatientDetailBinding
import com.nithin.healthapp.ui.common.AppointmentAdapter
import com.nithin.healthapp.util.DateUtils

class PatientDetailFragment : Fragment() {

    companion object {
        private const val ARG_PATIENT_ID = "patient_id"
        private const val ARG_PATIENT_NAME = "patient_name"
        private const val ARG_PATIENT_EMAIL = "patient_email"
        private const val ARG_PATIENT_CREATED = "patient_created"

        fun newInstance(id: Int, name: String, email: String, createdAt: String): PatientDetailFragment {
            return PatientDetailFragment().apply {
                arguments = Bundle().apply {
                    putInt(ARG_PATIENT_ID, id)
                    putString(ARG_PATIENT_NAME, name)
                    putString(ARG_PATIENT_EMAIL, email)
                    putString(ARG_PATIENT_CREATED, createdAt)
                }
            }
        }
    }

    private var _binding: FragmentPatientDetailBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

    private var patientId: Int = 0

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentPatientDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        patientId = arguments?.getInt(ARG_PATIENT_ID) ?: 0
        val patientName = arguments?.getString(ARG_PATIENT_NAME) ?: "Patient"
        val patientEmail = arguments?.getString(ARG_PATIENT_EMAIL) ?: ""
        val patientCreated = arguments?.getString(ARG_PATIENT_CREATED) ?: ""

        // Setup toolbar
        binding.toolbarDetail.title = patientName
        binding.toolbarDetail.setNavigationOnClickListener {
            parentFragmentManager.popBackStack()
        }

        // Patient info
        binding.tvPatientName.text = patientName
        binding.tvPatientEmail.text = patientEmail
        binding.tvPatientMeta.text = "ID: $patientId • Joined: ${DateUtils.formatDisplayDateTime(patientCreated)}"

        // Setup RecyclerViews
        binding.rvReports.layoutManager = LinearLayoutManager(requireContext())
        binding.rvDoctorAppointments.layoutManager = LinearLayoutManager(requireContext())
        binding.rvLabAppointments.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { loadData() }

        observeData()
        loadData()
    }

    private fun loadData() {
        viewModel.loadPatientReports(patientId)
        viewModel.loadPatientDoctorAppointments(patientId)
        viewModel.loadPatientLabAppointments(patientId)
    }

    private fun observeData() {
        viewModel.patientReports.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { reports ->
                if (reports.isEmpty()) {
                    binding.tvNoReports.visibility = View.VISIBLE
                    binding.rvReports.visibility = View.GONE
                } else {
                    binding.tvNoReports.visibility = View.GONE
                    binding.rvReports.visibility = View.VISIBLE
                    binding.rvReports.adapter = ReportDetailAdapter(reports) { report ->
                        viewModel.downloadReport(report.appointmentId)
                    }
                }
            }
            result.onFailure {
                binding.tvNoReports.visibility = View.VISIBLE
                binding.rvReports.visibility = View.GONE
            }
        }

        viewModel.patientDoctorAppointments.observe(viewLifecycleOwner) { result ->
            result.onSuccess { appointments ->
                if (appointments.isEmpty()) {
                    binding.tvNoDoctorAppts.visibility = View.VISIBLE
                    binding.rvDoctorAppointments.visibility = View.GONE
                } else {
                    binding.tvNoDoctorAppts.visibility = View.GONE
                    binding.rvDoctorAppointments.visibility = View.VISIBLE
                    val items = appointments.map { appt ->
                        AppointmentAdapter.AppointmentItem(
                            id = appt.id,
                            title = DateUtils.formatDisplayDateTime(appt.appointmentDate),
                            subtitle = appt.reason ?: "Consultation",
                            date = appt.appointmentDate,
                            status = appt.status,
                            type = "DOCTOR"
                        )
                    }
                    binding.rvDoctorAppointments.adapter = AppointmentAdapter(items)
                }
            }
            result.onFailure {
                binding.tvNoDoctorAppts.visibility = View.VISIBLE
                binding.rvDoctorAppointments.visibility = View.GONE
            }
        }

        viewModel.patientLabAppointments.observe(viewLifecycleOwner) { result ->
            result.onSuccess { appointments ->
                if (appointments.isEmpty()) {
                    binding.tvNoLabAppts.visibility = View.VISIBLE
                    binding.rvLabAppointments.visibility = View.GONE
                } else {
                    binding.tvNoLabAppts.visibility = View.GONE
                    binding.rvLabAppointments.visibility = View.VISIBLE
                    val items = appointments.map { appt ->
                        AppointmentAdapter.AppointmentItem(
                            id = appt.id,
                            title = appt.testType,
                            subtitle = "Lab #${appt.labId} • ${appt.reason ?: "No reason"}",
                            date = appt.appointmentDate,
                            status = appt.status,
                            type = "LAB"
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

        viewModel.downloadedFile.observe(viewLifecycleOwner) { result ->
            result.onSuccess { file ->
                try {
                    val uri = FileProvider.getUriForFile(
                        requireContext(),
                        "${requireContext().packageName}.fileprovider",
                        file
                    )
                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, "application/pdf")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }
                    startActivity(intent)
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "No PDF viewer found", Toast.LENGTH_SHORT).show()
                }
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Download failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
