package com.simats.cliniq.ui.lab

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.OpenableColumns
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.AutoCompleteTextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.textfield.TextInputEditText
import com.simats.cliniq.R
import com.simats.cliniq.data.models.LabAppointmentResponse
import com.simats.cliniq.databinding.FragmentLabReportsBinding
import com.simats.cliniq.ui.common.ReportAdapter
import com.simats.cliniq.util.DateUtils
import java.io.File
import java.io.FileOutputStream

class LabReportsFragment : Fragment() {

    private var _binding: FragmentLabReportsBinding? = null
    private val binding get() = _binding!!
    private val viewModel: LabViewModel by activityViewModels()

    private var selectedFileUri: Uri? = null
    private var selectedFileName: String? = null
    private var tvSelectedFile: android.widget.TextView? = null
    private var btnSelectFile: com.google.android.material.button.MaterialButton? = null
    private var cachedCompletedAppointments: List<LabAppointmentResponse> = emptyList()

    private val filePickerLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            result.data?.data?.let { uri ->
                selectedFileUri = uri
                selectedFileName = getFileName(uri) ?: "report.pdf"
                tvSelectedFile?.text = "Selected: $selectedFileName"
                tvSelectedFile?.setTextColor(resources.getColor(R.color.primary, null))
                btnSelectFile?.text = "Change PDF File"
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
                    binding.rvReports.adapter = ReportAdapter(
                        reports,
                        showDelete = true,
                        onItemClick = { report ->
                            MaterialAlertDialogBuilder(requireContext())
                                .setTitle("Delete Report")
                                .setMessage("Delete report '${report.fileName}'?")
                                .setPositiveButton("Delete") { _, _ ->
                                    viewModel.deleteReport(report.appointmentId)
                                }
                                .setNegativeButton("Cancel", null)
                                .show()
                        },
                        onDownloadClick = { report ->
                            viewModel.downloadReport(report.appointmentId)
                        }
                    )
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

        viewModel.labAppointments.observe(viewLifecycleOwner) { result ->
            result.onSuccess { appointments ->
                // Get the existing report appointment IDs to exclude them
                val existingReportApptIds = mutableSetOf<Int>()
                viewModel.reports.value?.getOrNull()?.forEach { report ->
                    existingReportApptIds.add(report.appointmentId)
                }
                cachedCompletedAppointments = appointments.filter {
                    it.status == "COMPLETED" && it.id !in existingReportApptIds
                }
            }
        }

        viewModel.loadReports()
        viewModel.loadAppointments()

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
    }

    private fun showUploadDialog() {
        selectedFileUri = null
        selectedFileName = null

        if (cachedCompletedAppointments.isEmpty()) {
            Toast.makeText(requireContext(), "No completed appointments available for upload", Toast.LENGTH_LONG).show()
            return
        }

        val dialogView = layoutInflater.inflate(R.layout.dialog_upload_report, null)
        val actvAppointment = dialogView.findViewById<AutoCompleteTextView>(R.id.actv_appointment)
        val etTestResults = dialogView.findViewById<TextInputEditText>(R.id.et_test_results)
        val etNotes = dialogView.findViewById<TextInputEditText>(R.id.et_notes)
        btnSelectFile = dialogView.findViewById(R.id.btn_select_file)
        tvSelectedFile = dialogView.findViewById(R.id.tv_selected_file)

        var selectedAppointmentId: Int? = null

        // Populate appointment dropdown
        val apptLabels = cachedCompletedAppointments.map { appt ->
            "#${appt.id} — ${appt.testType} (Patient #${appt.patientId}, ${DateUtils.formatDisplayDateTime(appt.appointmentDate)})"
        }
        val apptAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_dropdown_item_1line, apptLabels)
        actvAppointment.setAdapter(apptAdapter)
        actvAppointment.setOnItemClickListener { _, _, position, _ ->
            selectedAppointmentId = cachedCompletedAppointments[position].id
        }

        btnSelectFile?.setOnClickListener {
            openFilePicker()
        }

        val dialog = MaterialAlertDialogBuilder(requireContext())
            .setTitle("Upload Lab Report")
            .setView(dialogView)
            .setPositiveButton("Upload", null)
            .setNegativeButton("Cancel", null)
            .create()

        dialog.show()

        dialog.getButton(android.app.AlertDialog.BUTTON_POSITIVE).setOnClickListener {
            if (selectedAppointmentId == null) {
                Toast.makeText(requireContext(), "Select an appointment", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            if (selectedFileUri == null) {
                Toast.makeText(requireContext(), "Please select a PDF file", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            handleFileSelected(selectedFileUri!!, selectedAppointmentId!!, etTestResults.text?.toString(), etNotes.text?.toString())
            dialog.dismiss()
        }
    }

    private fun openFilePicker() {
        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "application/pdf"
            addCategory(Intent.CATEGORY_OPENABLE)
        }
        filePickerLauncher.launch(intent)
    }

    private fun handleFileSelected(uri: Uri, appointmentId: Int, testResults: String?, notes: String?) {
        try {
            val fileName = getFileName(uri) ?: "report.pdf"
            val tempFile = File(requireContext().cacheDir, fileName)

            requireContext().contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(tempFile).use { output ->
                    input.copyTo(output)
                }
            }

            viewModel.uploadReport(appointmentId, tempFile, testResults, notes)
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
