package com.simats.cliniq.ui.doctor

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.simats.cliniq.R
import com.simats.cliniq.databinding.FragmentDoctorQueriesBinding
import com.simats.cliniq.ui.common.QueryAdapter

class DoctorQueriesFragment : Fragment() {

    private var _binding: FragmentDoctorQueriesBinding? = null
    private val binding get() = _binding!!
    private val viewModel: DoctorViewModel by activityViewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentDoctorQueriesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvQueries.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { viewModel.loadQueries() }

        viewModel.queries.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { queries ->
                if (queries.isEmpty()) {
                    binding.tvNoQueries.visibility = View.VISIBLE
                    binding.rvQueries.visibility = View.GONE
                } else {
                    binding.tvNoQueries.visibility = View.GONE
                    binding.rvQueries.visibility = View.VISIBLE
                    binding.rvQueries.adapter = QueryAdapter(queries, isDoctor = true) { query ->
                        if (!query.isResponded) {
                            showRespondDialog(query)
                        }
                    }
                }
            }
            result.onFailure {
                binding.tvNoQueries.visibility = View.VISIBLE
                binding.rvQueries.visibility = View.GONE
            }
        }

        viewModel.respondResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Response sent!", Toast.LENGTH_SHORT).show()
                viewModel.loadQueries()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Error: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loadQueries()
    }

    private fun showRespondDialog(query: com.simats.cliniq.data.models.QueryResponse) {
        val dialogView = layoutInflater.inflate(R.layout.dialog_respond_query, null)
        val etResponse = dialogView.findViewById<TextInputEditText>(R.id.et_response)

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Respond to Query")
            .setMessage("Patient's question:\n\"${query.queryText}\"")
            .setView(dialogView)
            .setPositiveButton("Send") { _, _ ->
                val text = etResponse.text?.toString()?.trim()
                if (text.isNullOrEmpty()) {
                    Toast.makeText(requireContext(), "Response cannot be empty", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                viewModel.respondToQuery(query.id, text)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
