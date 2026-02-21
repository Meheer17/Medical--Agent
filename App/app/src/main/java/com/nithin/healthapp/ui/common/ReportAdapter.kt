package com.nithin.healthapp.ui.common

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.cardview.widget.CardView
import androidx.recyclerview.widget.RecyclerView
import com.nithin.healthapp.R
import com.nithin.healthapp.data.models.LabReportResponse
import com.nithin.healthapp.util.DateUtils

class ReportAdapter(
    private val reports: List<LabReportResponse>,
    private val showDelete: Boolean = false,
    private val onItemClick: ((LabReportResponse) -> Unit)? = null,
    private val onDownloadClick: ((LabReportResponse) -> Unit)? = null
) : RecyclerView.Adapter<ReportAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val card: CardView = view.findViewById(R.id.card_report)
        val tvFileName: TextView = view.findViewById(R.id.tv_file_name)
        val tvAppointmentId: TextView = view.findViewById(R.id.tv_appointment_id)
        val tvStatus: TextView = view.findViewById(R.id.tv_ai_status)
        val tvSummary: TextView = view.findViewById(R.id.tv_summary)
        val tvDate: TextView = view.findViewById(R.id.tv_date)
        val tvFileSize: TextView = view.findViewById(R.id.tv_file_size)
        val btnViewPdf: com.google.android.material.button.MaterialButton = view.findViewById(R.id.btn_view_pdf)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_report, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val report = reports[position]
        holder.tvFileName.text = report.fileName
        holder.tvAppointmentId.text = "Appointment #${report.appointmentId}"
        holder.tvDate.text = DateUtils.formatDisplayDate(report.createdAt)

        val fileSizeKb = report.fileSize / 1024
        holder.tvFileSize.text = if (fileSizeKb > 1024) "${fileSizeKb / 1024} MB" else "$fileSizeKb KB"

        when (report.aiAnalysisStatus) {
            "COMPLETED" -> {
                holder.tvStatus.text = "✅ AI Analysis Complete"
                holder.tvStatus.setTextColor(android.graphics.Color.parseColor("#4CAF50"))
                holder.tvSummary.text = report.aiSummary ?: "View details for analysis"
                holder.tvSummary.visibility = View.VISIBLE
            }
            "PENDING" -> {
                holder.tvStatus.text = "⏳ AI Analysis Pending"
                holder.tvStatus.setTextColor(android.graphics.Color.parseColor("#FF9800"))
                holder.tvSummary.text = "Processing report..."
                holder.tvSummary.visibility = View.VISIBLE
            }
            "FAILED" -> {
                holder.tvStatus.text = "❌ AI Analysis Failed"
                holder.tvStatus.setTextColor(android.graphics.Color.parseColor("#F44336"))
                holder.tvSummary.text = report.aiAnalysisError ?: "Analysis could not be completed"
                holder.tvSummary.visibility = View.VISIBLE
            }
            else -> {
                holder.tvStatus.text = report.aiAnalysisStatus
                holder.tvSummary.visibility = View.GONE
            }
        }

        holder.card.setOnClickListener {
            onItemClick?.invoke(report)
        }

        if (onDownloadClick != null) {
            holder.btnViewPdf.visibility = View.VISIBLE
            holder.btnViewPdf.setOnClickListener {
                onDownloadClick.invoke(report)
            }
        } else {
            holder.btnViewPdf.visibility = View.GONE
        }
    }

    override fun getItemCount() = reports.size
}
