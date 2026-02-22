package com.simats.cliniq.ui.patient

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
import com.simats.cliniq.databinding.FragmentPatientReportsBinding
import com.simats.cliniq.ui.common.ReportAdapter

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
                    binding.rvReports.adapter = ReportAdapter(
                        reports,
                        onItemClick = { report -> showReportDetail(report) },
                        onDownloadClick = { report -> viewModel.downloadReport(report.appointmentId) }
                    )
                }
            }
            result.onFailure {
                binding.tvNoReports.visibility = View.VISIBLE
                binding.rvReports.visibility = View.GONE
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.downloadedFile.observe(viewLifecycleOwner) { result ->
            result.onSuccess { file ->
                val uri = FileProvider.getUriForFile(
                    requireContext(),
                    "${requireContext().packageName}.fileprovider",
                    file
                )
                val intent = Intent(Intent.ACTION_VIEW).apply {
                    setDataAndType(uri, "application/pdf")
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }
                try {
                    startActivity(intent)
                } catch (e: Exception) {
                    Toast.makeText(requireContext(), "No PDF viewer found", Toast.LENGTH_SHORT).show()
                }
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Download failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loadReports()
    }

    private fun showReportDetail(report: com.simats.cliniq.data.models.LabReportResponse) {
        val dialog = com.google.android.material.dialog.MaterialAlertDialogBuilder(requireContext())
            .setTitle("Report: ${report.fileName}")
            .setMessage(buildReportSummary(report))
            .setPositiveButton("Close", null)
            .create()
        dialog.show()
    }

    private fun buildReportSummary(report: com.simats.cliniq.data.models.LabReportResponse): String {
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
