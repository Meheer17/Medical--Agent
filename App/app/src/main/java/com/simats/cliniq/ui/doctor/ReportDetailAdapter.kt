package com.simats.cliniq.ui.doctor

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.button.MaterialButton
import com.google.android.material.chip.Chip
import com.simats.cliniq.R
import com.simats.cliniq.data.models.LabReportResponse
import com.simats.cliniq.util.DateUtils
import org.json.JSONArray

class ReportDetailAdapter(
    private val reports: List<LabReportResponse>,
    private val onDownloadClick: (LabReportResponse) -> Unit
) : RecyclerView.Adapter<ReportDetailAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvFileName: TextView = view.findViewById(R.id.tv_report_file_name)
        val tvDate: TextView = view.findViewById(R.id.tv_report_date)
        val btnDownload: MaterialButton = view.findViewById(R.id.btn_download)
        val chipStatus: Chip = view.findViewById(R.id.chip_status)
        val tvSummaryLabel: TextView = view.findViewById(R.id.tv_summary_label)
        val tvSummary: TextView = view.findViewById(R.id.tv_summary)
        val tvFindingsLabel: TextView = view.findViewById(R.id.tv_findings_label)
        val tvFindings: TextView = view.findViewById(R.id.tv_findings)
        val tvAbnormalLabel: TextView = view.findViewById(R.id.tv_abnormal_label)
        val tvAbnormal: TextView = view.findViewById(R.id.tv_abnormal)
        val tvSignificanceLabel: TextView = view.findViewById(R.id.tv_significance_label)
        val tvSignificance: TextView = view.findViewById(R.id.tv_significance)
        val tvRecommendationLabel: TextView = view.findViewById(R.id.tv_recommendation_label)
        val tvRecommendation: TextView = view.findViewById(R.id.tv_recommendation)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_report_detail, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val report = reports[position]

        holder.tvFileName.text = report.fileName
        holder.tvDate.text = DateUtils.formatDisplayDateTime(report.createdAt)

        holder.btnDownload.setOnClickListener { onDownloadClick(report) }

        // Status chip
        when (report.aiAnalysisStatus) {
            "completed" -> {
                holder.chipStatus.text = "AI Analysis Complete"
                holder.chipStatus.setChipBackgroundColorResource(R.color.status_completed)
            }
            "pending" -> {
                holder.chipStatus.text = "Analysis Pending..."
                holder.chipStatus.setChipBackgroundColorResource(R.color.status_scheduled)
            }
            else -> {
                holder.chipStatus.text = "Analysis Failed"
                holder.chipStatus.setChipBackgroundColorResource(R.color.status_cancelled)
            }
        }

        // AI Summary
        showFieldIfPresent(holder.tvSummaryLabel, holder.tvSummary, report.aiSummary)

        // Key Findings - parse JSON array
        showFieldIfPresent(holder.tvFindingsLabel, holder.tvFindings, parseJsonArray(report.aiKeyFindings))

        // Abnormal Values
        showFieldIfPresent(holder.tvAbnormalLabel, holder.tvAbnormal, parseJsonArray(report.aiAbnormalValues))

        // Clinical Significance
        showFieldIfPresent(holder.tvSignificanceLabel, holder.tvSignificance, report.aiClinicalSignificance)

        // Recommendation
        showFieldIfPresent(holder.tvRecommendationLabel, holder.tvRecommendation, report.aiDoctorRecommendation)
    }

    private fun showFieldIfPresent(label: TextView, value: TextView, text: String?) {
        if (!text.isNullOrBlank()) {
            label.visibility = View.VISIBLE
            value.visibility = View.VISIBLE
            value.text = text
        } else {
            label.visibility = View.GONE
            value.visibility = View.GONE
        }
    }

    private fun parseJsonArray(jsonStr: String?): String? {
        if (jsonStr.isNullOrBlank()) return null
        return try {
            val arr = JSONArray(jsonStr)
            if (arr.length() == 0) return null
            buildString {
                for (i in 0 until arr.length()) {
                    if (i > 0) append("\n")
                    append("• ${arr.getString(i)}")
                }
            }
        } catch (e: Exception) {
            jsonStr
        }
    }

    override fun getItemCount() = reports.size
}
