package com.nithin.healthapp.ui.common

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.cardview.widget.CardView
import androidx.recyclerview.widget.RecyclerView
import com.nithin.healthapp.R
import com.nithin.healthapp.util.DateUtils

class AppointmentAdapter(
    private val items: List<AppointmentItem>,
    private val onItemClick: ((AppointmentItem) -> Unit)? = null
) : RecyclerView.Adapter<AppointmentAdapter.ViewHolder>() {

    data class AppointmentItem(
        val id: Int,
        val title: String,
        val subtitle: String,
        val date: String,
        val status: String,
        val type: String  // "DOCTOR" or "LAB"
    )

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val card: CardView = view.findViewById(R.id.card_appointment)
        val tvTitle: TextView = view.findViewById(R.id.tv_title)
        val tvSubtitle: TextView = view.findViewById(R.id.tv_subtitle)
        val tvDate: TextView = view.findViewById(R.id.tv_date)
        val tvTime: TextView = view.findViewById(R.id.tv_time)
        val tvStatus: TextView = view.findViewById(R.id.tv_status)
        val tvType: TextView = view.findViewById(R.id.tv_type)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_appointment, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.tvTitle.text = item.title
        holder.tvSubtitle.text = item.subtitle
        holder.tvDate.text = DateUtils.formatDisplayDate(item.date)
        holder.tvTime.text = DateUtils.formatDisplayTime(item.date)
        holder.tvStatus.text = item.status.replaceFirstChar { it.uppercase() }
        holder.tvStatus.setTextColor(DateUtils.getStatusColor(item.status))
        holder.tvType.text = if (item.type == "doctor") "🩺 Doctor" else "🔬 Lab"

        holder.card.setOnClickListener {
            onItemClick?.invoke(item)
        }
    }

    override fun getItemCount() = items.size
}
