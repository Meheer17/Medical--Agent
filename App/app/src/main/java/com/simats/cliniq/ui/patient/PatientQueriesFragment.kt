package com.simats.cliniq.ui.patient

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.MaterialAutoCompleteTextView
import com.google.android.material.textfield.TextInputEditText
import com.simats.cliniq.R
import com.simats.cliniq.databinding.FragmentPatientQueriesBinding
import com.simats.cliniq.ui.common.QueryAdapter

class PatientQueriesFragment : Fragment() {

    private var _binding: FragmentPatientQueriesBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PatientViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentPatientQueriesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvQueries.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { viewModel.loadQueries() }

        binding.fabCreateQuery.setOnClickListener { showCreateQueryDialog() }

        viewModel.queries.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { queries ->
                if (queries.isEmpty()) {
                    binding.tvNoQueries.visibility = View.VISIBLE
                    binding.rvQueries.visibility = View.GONE
                } else {
                    binding.tvNoQueries.visibility = View.GONE
                    binding.rvQueries.visibility = View.VISIBLE
                    binding.rvQueries.adapter = QueryAdapter(queries, isDoctor = false)
                }
            }
            result.onFailure {
                binding.tvNoQueries.visibility = View.VISIBLE
                binding.rvQueries.visibility = View.GONE
            }
        }

        viewModel.queryCreate.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Query sent!", Toast.LENGTH_SHORT).show()
                viewModel.loadQueries()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_LONG).show()
            }
        }

        viewModel.loadQueries()
    }

    private fun showCreateQueryDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_create_query, null)
        val etQuery = dialogView.findViewById<TextInputEditText>(R.id.et_query_text)
        val actvUrgency = dialogView.findViewById<MaterialAutoCompleteTextView>(R.id.actv_urgency)

        val urgencies = listOf("LOW", "MEDIUM", "HIGH")
        val urgencyLabels = listOf("Low", "Medium", "High")
        actvUrgency.setAdapter(ArrayAdapter(requireContext(), R.layout.item_dropdown, urgencyLabels))
        actvUrgency.setText("Medium", false)

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Send Query to Doctor")
            .setView(dialogView)
            .setPositiveButton("Send") { _, _ ->
                val text = etQuery.text?.toString()?.trim()
                if (text.isNullOrEmpty()) {
                    Toast.makeText(requireContext(), "Query text is required", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                val idx = urgencyLabels.indexOf(actvUrgency.text.toString())
                val urgency = if (idx >= 0) urgencies[idx] else "MEDIUM"
                viewModel.createQuery(text, urgency)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
