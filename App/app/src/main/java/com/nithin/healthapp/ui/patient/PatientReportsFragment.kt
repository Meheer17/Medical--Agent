package com.nithin.healthapp.ui.patient

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.nithin.healthapp.databinding.FragmentPatientReportsBinding
import com.nithin.healthapp.ui.common.ReportAdapter

class PatientReportsFragment : Fragment() {

    private var _binding: FragmentPatientReportsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentPatientReportsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvReports.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadReports()
        }

        viewModel.reports.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { reports ->
                if (reports.isEmpty()) {
                    binding.tvNoReports.visibility = View.VISIBLE
                    binding.rvReports.visibility = View.GONE
                } else {
                    binding.tvNoReports.visibility = View.GONE
                    binding.rvReports.visibility = View.VISIBLE
                    binding.rvReports.adapter = ReportAdapter(reports) { report ->
                        showReportDetail(report)
                    }
                }
            }
            result.onFailure {
                binding.tvNoReports.visibility = View.VISIBLE
                binding.rvReports.visibility = View.GONE
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loadReports()
    }

    private fun showReportDetail(report: com.nithin.healthapp.data.models.LabReportResponse) {
        val dialog = com.google.android.material.dialog.MaterialAlertDialogBuilder(requireContext())
            .setTitle("Report: ${report.fileName}")
            .setMessage(buildReportSummary(report))
            .setPositiveButton("Close", null)
            .create()
        dialog.show()
    }

    private fun buildReportSummary(report: com.nithin.healthapp.data.models.LabReportResponse): String {
        val sb = StringBuilder()
        sb.appendLine("Status: ${report.aiAnalysisStatus}")
        sb.appendLine()

        if (report.aiSummary != null) {
            sb.appendLine("📋 AI Summary:")
            sb.appendLine(report.aiSummary)
            sb.appendLine()
        }

        if (report.aiKeyFindings != null) {
            sb.appendLine("🔍 Key Findings:")
            sb.appendLine(report.aiKeyFindings)
            sb.appendLine()
        }

        if (report.aiAbnormalValues != null) {
            sb.appendLine("⚠️ Abnormal Values:")
            sb.appendLine(report.aiAbnormalValues)
            sb.appendLine()
        }

        if (report.aiClinicalSignificance != null) {
            sb.appendLine("🏥 Clinical Significance:")
            sb.appendLine(report.aiClinicalSignificance)
            sb.appendLine()
        }

        if (report.aiDoctorRecommendation != null) {
            sb.appendLine("👨‍⚕️ Doctor Recommendation:")
            sb.appendLine(report.aiDoctorRecommendation)
        }

        if (report.testResults != null) {
            sb.appendLine()
            sb.appendLine("📝 Test Results: ${report.testResults}")
        }

        return sb.toString()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
