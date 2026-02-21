package com.nithin.healthapp.ui.lab

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.nithin.healthapp.R
import com.nithin.healthapp.databinding.FragmentLabReportsBinding
import com.nithin.healthapp.ui.common.ReportAdapter
import java.io.File
import java.io.FileOutputStream

class LabReportsFragment : Fragment() {

    private var _binding: FragmentLabReportsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: LabViewModel by activityViewModels()

    private var pendingAppointmentId: Int? = null
    private var pendingTestResults: String? = null
    private var pendingNotes: String? = null

    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            result.data?.data?.let { uri ->
                handleFileSelected(uri)
            }
        }
    }

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        _binding = FragmentLabReportsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        binding.rvReports.layoutManager = LinearLayoutManager(requireContext())

        binding.swipeRefresh.setOnRefreshListener { viewModel.loadReports() }
        binding.fabUploadReport.setOnClickListener { showUploadDialog() }

        viewModel.reports.observe(viewLifecycleOwner) { result ->
            binding.swipeRefresh.isRefreshing = false
            result.onSuccess { reports ->
                if (reports.isEmpty()) {
                    binding.tvNoReports.visibility = View.VISIBLE
                    binding.rvReports.visibility = View.GONE
                } else {
                    binding.tvNoReports.visibility = View.GONE
                    binding.rvReports.visibility = View.VISIBLE
                    binding.rvReports.adapter = ReportAdapter(reports, showDelete = true) { report ->
                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle("Delete Report")
                            .setMessage("Delete report '${report.fileName}'?")
                            .setPositiveButton("Delete") { _, _ ->
                                viewModel.deleteReport(report.appointmentId)
                            }
                            .setNegativeButton("Cancel", null)
                            .show()
                    }
                }
            }
            result.onFailure {
                binding.tvNoReports.visibility = View.VISIBLE
                binding.rvReports.visibility = View.GONE
            }
        }

        viewModel.uploadResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Report uploaded! AI analysis in progress...", Toast.LENGTH_LONG).show()
                viewModel.loadReports()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Upload failed: ${it.message}", Toast.LENGTH_LONG).show()
            }
        }

        viewModel.deleteResult.observe(viewLifecycleOwner) { result ->
            result.onSuccess {
                Toast.makeText(requireContext(), "Report deleted", Toast.LENGTH_SHORT).show()
                viewModel.loadReports()
            }
            result.onFailure {
                Toast.makeText(requireContext(), "Delete failed: ${it.message}", Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.loadReports()
    }

    private fun showUploadDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_upload_report, null)
        val etAppointmentId = dialogView.findViewById<TextInputEditText>(R.id.et_appointment_id)
        val etTestResults = dialogView.findViewById<TextInputEditText>(R.id.et_test_results)
        val etNotes = dialogView.findViewById<TextInputEditText>(R.id.et_notes)

        MaterialAlertDialogBuilder(requireContext())
            .setTitle("Upload Lab Report")
            .setView(dialogView)
            .setPositiveButton("Choose PDF") { _, _ ->
                val appointmentId = etAppointmentId.text.toString().toIntOrNull()
                if (appointmentId == null) {
                    Toast.makeText(requireContext(), "Enter valid appointment ID", Toast.LENGTH_SHORT).show()
                    return@setPositiveButton
                }
                pendingAppointmentId = appointmentId
                pendingTestResults = etTestResults.text?.toString()
                pendingNotes = etNotes.text?.toString()
                openFilePicker()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "application/pdf"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        filePickerLauncher.launch(intent)
    }

    private fun handleFileSelected(uri: Uri) {
        val appointmentId = pendingAppointmentId ?: return

        try {
            val fileName = getFileName(uri) ?: "report.pdf"
            val tempFile = File(requireContext().cacheDir, fileName)

            requireContext().contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(tempFile).use { output ->
                    input.copyTo(output)
                }
            }

            viewModel.uploadReport(appointmentId, tempFile, pendingTestResults, pendingNotes)
        } catch (e: Exception) {
            Toast.makeText(requireContext(), "Error reading file: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private fun getFileName(uri: Uri): String? {
        var name: String? = null
        requireContext().contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            val nameIndex = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            cursor.moveToFirst()
            name = cursor.getString(nameIndex)
        }
        return name
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
