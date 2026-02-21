package com.nithin.healthapp.ui.common

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.cardview.widget.CardView
import androidx.recyclerview.widget.RecyclerView
import com.nithin.healthapp.R
import com.nithin.healthapp.data.models.QueryResponse
import com.nithin.healthapp.util.DateUtils

class QueryAdapter(
    private val queries: List<QueryResponse>,
    private val isDoctor: Boolean = false,
    private val onItemClick: ((QueryResponse) -> Unit)? = null
) : RecyclerView.Adapter<QueryAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val card: CardView = view.findViewById(R.id.card_query)
        val tvQuery: TextView = view.findViewById(R.id.tv_query_text)
        val tvResponse: TextView = view.findViewById(R.id.tv_response_text)
        val tvUrgency: TextView = view.findViewById(R.id.tv_urgency)
        val tvStatus: TextView = view.findViewById(R.id.tv_status)
        val tvDate: TextView = view.findViewById(R.id.tv_date)
        val tvParty: TextView = view.findViewById(R.id.tv_party)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_query, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val query = queries[position]
        holder.tvQuery.text = query.queryText
        holder.tvDate.text = DateUtils.formatDisplayDateTime(query.createdAt)
        holder.tvUrgency.text = query.urgency.replaceFirstChar { it.uppercase() }
        holder.tvUrgency.setTextColor(DateUtils.getUrgencyColor(query.urgency))

        holder.tvParty.text = if (isDoctor) "Patient #${query.patientId}" else "To Doctor #${query.doctorId}"

        if (query.isResponded) {
            holder.tvStatus.text = "✅ Responded"
            holder.tvStatus.setTextColor(android.graphics.Color.parseColor("#4CAF50"))
            holder.tvResponse.text = "Response: ${query.responseText}"
            holder.tvResponse.visibility = View.VISIBLE
        } else {
            holder.tvStatus.text = if (isDoctor) "⏳ Awaiting your response" else "⏳ Awaiting response"
            holder.tvStatus.setTextColor(android.graphics.Color.parseColor("#FF9800"))
            holder.tvResponse.visibility = View.GONE
        }

        holder.card.setOnClickListener {
            onItemClick?.invoke(query)
        }
    }

    override fun getItemCount() = queries.size
}
