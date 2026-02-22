package com.simats.cliniq.ui.common

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.simats.cliniq.R
import com.simats.cliniq.data.models.UserResponse

class PatientAdapter(
    private val patients: List<UserResponse>,
    private val onItemClick: ((UserResponse) -> Unit)? = null
) : RecyclerView.Adapter<PatientAdapter.ViewHolder>() {

    inner class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvName: TextView = view.findViewById(R.id.tv_patient_name)
        val tvEmail: TextView = view.findViewById(R.id.tv_patient_email)
        val tvId: TextView = view.findViewById(R.id.tv_patient_id)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_patient, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val patient = patients[position]
        holder.tvName.text = patient.fullName ?: patient.username
        holder.tvEmail.text = patient.email
        holder.tvId.text = "ID: ${patient.id}"

        holder.itemView.setOnClickListener {
            onItemClick?.invoke(patient)
        }
    }

    override fun getItemCount() = patients.size
}
